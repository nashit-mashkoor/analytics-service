import asyncio
import os
import io
import sys
import statistics
import json
import numpy as np

from analytics_utils.logging import Logging
from analytics_utils.date import to_datetime, to_unix_timestamp, update_datetime_by_seconds
from pipelines.pipeline_exception import PipelineExceptions
from scipy.signal import medfilt
from services.mongodb.database import Database
from services.annotation import get_annotations_by_id, start_annotation_validation, \
                                update_annotation_validation_status, \
                                get_annotation_validation_status, ValidationStatus
from services.telemetry import to_csv
from services.cloud_storage import CloudStorage


sys.path.append(os.path.dirname(os.path.realpath(__file__)))

logging_instance = Logging()
logger = logging_instance.get_logger()

# Helpers
async def _get_telemetry(serial_number, from_date, to_date, collection_name="TelemetryLog", query=None):
    if query is None:
        query = [
            {
                "$match": {
                    "sn": "$serialNumbers",
                    "payloadCreateAt":  {"$gte": "$fromDate", "$lte": "$toDate"},
                }
            },
            {
                "$sort": {
                    "payloadCreateAt": 1
                }
            }
        ]

    query_params = {
        "serialNumbers": serial_number,
        "fromDate": from_date,
        "toDate": to_date,
    }
    mongo_db = Database()
    collection = mongo_db.get_collection(collection_name)
    aggregation_pipeline = mongo_db.render_mongo_aggregation_object(
        query, query_params
    )
    return list(collection.aggregate(aggregation_pipeline))

# Processors
async def get_annotation(pipeline_config, params, data):
    annotationId = params["annotationId"]
    annotation = await get_annotations_by_id(annotationId)
    result = {
        "annotationId": annotationId,
        "annotationConfigurationId": annotation["configuration"].get("uuid", None),
        "annotationMetadataDetails": annotation["metadata"].get("details", {}),
        "annotationIdentities": annotation["identities"],
        "annotationCreatedAt": annotation["createdAt"],
        "events": annotation["events"],
        "serialNumbers": annotation["deviceSerialNumbers"],
    }
    return result


async def get_event_telemetry(pipeline_config, params, data):
    # Get other pipeline steps result
    serial_number = data[pipeline_config["annotationSerialNumber"]["origin"]][
        pipeline_config["annotationSerialNumber"]["name"]
    ]["serialNumbers"][0]
    events = data[pipeline_config["annotationEvents"]["origin"]][
        pipeline_config["annotationEvents"]["name"]
    ]["events"]
    collection_name = pipeline_config["collection"]
    query = pipeline_config["query"]
    for i in range(len(events) - 1):
        current_event = events[i]
        next_event = events[i + 1]

        current_created_at = to_datetime(current_event["createdAt"])
        next_created_at = to_datetime(next_event["createdAt"])

        telemetry = await _get_telemetry(serial_number=serial_number, from_date=current_created_at, to_date=next_created_at, collection_name=collection_name, query=query)
        events[i]["telemetry"] = telemetry

    result = {"events": events}
    return result


async def generate_file(pipeline_config, params, data):
    file_type = pipeline_config["fileType"]
    serial_number = data[pipeline_config["serialNumbers"]["origin"]][
        pipeline_config["serialNumbers"]["name"]
    ]["serialNumbers"][0]
    annotationId = data[pipeline_config["annotationId"]["origin"]][
        pipeline_config["annotationId"]["name"]
    ]["annotationId"]
    annotationConfigurationId = data[
        pipeline_config["annotationConfigurationId"]["origin"]
    ][pipeline_config["annotationConfigurationId"]["name"]][
        "annotationConfigurationId"
    ]
    annotationMetadataDetails = data[
        pipeline_config["annotationMetadataDetails"]["origin"]
    ][pipeline_config["annotationMetadataDetails"]["name"]][
        "annotationMetadataDetails"
    ]
    annotationIdentities = data[pipeline_config["annotationIdentities"]["origin"]][
        pipeline_config["annotationIdentities"]["name"]
    ]["annotationIdentities"]
    annotationCreatedAt = data[pipeline_config["annotationCreatedAt"]["origin"]][
        pipeline_config["annotationCreatedAt"]["name"]
    ]["annotationCreatedAt"]
    events = data[pipeline_config["eventsTelemetryData"]["origin"]][
        pipeline_config["eventsTelemetryData"]["name"]
    ]["events"]

    path = f"annotations_aggregator/{annotationCreatedAt}"
    if not os.path.exists(path):
        os.makedirs(path)

    if file_type == "json":
        file_output_path = f"{path}/{annotationId}_{serial_number}.json"
        with io.open(file_output_path, "w") as f:
            json.dump(events, f, default=str, indent=2)

    elif file_type == "csv":
        file_output_path = f"{path}/{annotationId}_{serial_number}.csv"
        with open(file_output_path, mode="w", newline="") as file:
            # Write the contents to the file
            csv_file = to_csv(
                annotationId,
                annotationConfigurationId,
                annotationMetadataDetails,
                annotationIdentities,
                events,
            )
            if csv_file:
                file.write(csv_file)

    result = {"file": file_output_path}
    return result


async def upload_to_gcp(pipeline_config, params, data):
    file_path = data[pipeline_config["uploadFile"]["origin"]][
        pipeline_config["uploadFile"]["name"]
    ]["file"]
    createdAt = data[pipeline_config["annotationCreatedAt"]["origin"]][
        pipeline_config["annotationCreatedAt"]["name"]
    ]["annotationCreatedAt"]
    file_name = file_path.split("/")[-1]
    destination_path = os.path.join(
        pipeline_config["path"], createdAt, file_name)
    bucket_name = pipeline_config.get("bucket_name", None)

    CloudStorage().upload_file(destination_path, file_path, bucket_name)
    result = {"data": True}
    return result

# Validation Processors
# static_validation
async def max_consecutive_dropped_payload(pipeline_config, params, data):
    events = data[pipeline_config["eventsTelemetryData"]["origin"]][
        pipeline_config["eventsTelemetryData"]["name"]
    ]["events"]
    sampling_rate = pipeline_config["sampling_rate"]
    mcdp_threshold = pipeline_config["mcdp_threshold"]

    telemetry_timestamps = [
        to_unix_timestamp(telemetry.get("d", ""))
        for event in events
        for telemetry in event.get("telemetry", [])
    ]

    if not telemetry_timestamps:
        return {"status": False, "validator": "STATIC_VALIDATE"}

    max_diff = max(
        [b - a for a, b in zip(telemetry_timestamps,
                               telemetry_timestamps[1:])]
    )
    status = (mcdp_threshold * sampling_rate - max_diff) > 0

    result = {"status": status, "validator": "STATIC_VALIDATE"}
    return result


async def median_consecutive_time_delta(pipeline_config, params, data):
    events = data[pipeline_config["eventsTelemetryData"]["origin"]][
        pipeline_config["eventsTelemetryData"]["name"]
    ]["events"]
    sampling_rate = pipeline_config["sampling_rate"]
    mdt_threshold = pipeline_config["mdt_threshold"]

    telemetry_timestamps = [
        to_unix_timestamp(telemetry.get("d", ""))
        for event in events
        for telemetry in event.get("telemetry", [])
    ]

    if telemetry_timestamps == []:
        return {"status": False, "validator": "STATIC_VALIDATE"}

    time_deltas = [b - a for a,
                   b in zip(telemetry_timestamps, telemetry_timestamps[1:])]
    median_diff = statistics.median(time_deltas)
    status = median_diff < (
        mdt_threshold + 1 / sampling_rate)

    result = {"status": status, "validator": "STATIC_VALIDATE"}
    return result


async def min_session_completeness(pipeline_config, params, data):
    events = data[pipeline_config["eventsTelemetryData"]["origin"]][
        pipeline_config["eventsTelemetryData"]["name"]
    ]["events"]
    sampling_rate = pipeline_config["sampling_rate"]
    msc_threshold = pipeline_config["msc_threshold"]

    telemetry_timestamps = [to_unix_timestamp(telemetry.get(
        "d", "")) for event in events for telemetry in event.get("telemetry", [])]

    if not telemetry_timestamps:
        return {"status": False, "validator": "STATIC_VALIDATE"}

    session_start_times = [to_unix_timestamp(
        event["createdAt"]) for event in events]
    session_duration = session_start_times[-1] - session_start_times[0]

    sampling_rate_ratio = session_duration / sampling_rate
    status = ((sampling_rate_ratio - len(telemetry_timestamps)) /
              sampling_rate_ratio - msc_threshold) > 0

    result = {"status": status, "validator": "STATIC_VALIDATE"}
    return result


async def interval_connectivity_verification(pipeline_config, params, data):
    events = data[pipeline_config["eventsTelemetryData"]["origin"]][
        pipeline_config["eventsTelemetryData"]["name"]
    ]["events"]
    all_event_names = {event["name"] for event in events}
    interval_names = set(pipeline_config["interval_names"])

    if not interval_names or not interval_names.issubset(all_event_names):
        return {"status": False, "validator": "STATIC_VALIDATE"}

    maxdt_threshold = pipeline_config["maxdt_threshold"]
    large_gaps_threshold_interval = pipeline_config["large_gaps_threshold_interval"]
    acceptable_num_gaps_interval = pipeline_config["acceptable_num_gaps_interval"]
    percentage_available_interval = pipeline_config["percentage_available_interval"]
    sampling_rate = pipeline_config["sampling_rate"]

    interval_timestamps = {
        prev_event["name"]: to_unix_timestamp(
            event["createdAt"]) - to_unix_timestamp(prev_event["createdAt"])
        for prev_event, event in zip(events, events[1:])
    }
    interval_duration = sum(interval_timestamps.get(
        interval_name, 0) for interval_name in interval_names)

    telemetry_timestamps = [
        to_unix_timestamp(telemetry.get("d", ""))
        for event in events
        for telemetry in event.get("telemetry", [])
        if event.get("name", "") in interval_names
    ]

    if not telemetry_timestamps:
        return {"status": False, "validator": "STATIC_VALIDATE"}
    telemetry_timestamps_diff = [
        b - a for a, b in zip(telemetry_timestamps, telemetry_timestamps[1:])]

    max_diff = max(telemetry_timestamps_diff)
    max_diff_status = max_diff < maxdt_threshold

    large_gaps_status = len(
        [timestamp_diff > large_gaps_threshold_interval for timestamp_diff in telemetry_timestamps_diff]) < acceptable_num_gaps_interval

    data_points_status = len(telemetry_timestamps) >= (
        percentage_available_interval * interval_duration * sampling_rate)

    status = max_diff_status and large_gaps_status and data_points_status
    result = {"status": status, "validator": "STATIC_VALIDATE"}
    return result


async def stability_of_reference_sensing_elements(pipeline_config, params, data):
    events = data[pipeline_config["eventsTelemetryData"]["origin"]][
        pipeline_config["eventsTelemetryData"]["name"]
    ]["events"]
    serial_number = data[pipeline_config["serialNumber"]["origin"]][
        pipeline_config["serialNumber"]["name"]
    ]["serialNumbers"][0]
    event_created_at = {event["name"]: event["createdAt"] for event in events}

    if "Exposure" not in event_created_at:
        return {"status": False, "validator": "STATIC_VALIDATE"}
    exposure_created_at = to_datetime(event_created_at["Exposure"])

    verification_interval_seconds = pipeline_config["verification_interval_seconds"]

    interval_start = update_datetime_by_seconds(
        exposure_created_at, verification_interval_seconds)
    interval_end = exposure_created_at

    telemetries = await _get_telemetry(serial_number, interval_start, interval_end)

    reference_sensing_elements = pipeline_config["reference_sensing_elements"]

    combined_sensor_elements = {ref_sense_elem["name"]: [
    ] for ref_sense_elem in reference_sensing_elements}
    for reference_sensing_element in reference_sensing_elements:
        sensor_element = reference_sensing_element["name"]
        sensor_threshold = reference_sensing_element["threshold"]

        for telemetry in telemetries:
            sensor_values = telemetry.get(telemetry["sn"], {})
            sensor_value = sensor_values.get(sensor_element, 0)
            combined_sensor_elements[sensor_element].append(sensor_value)

        sensor_values = combined_sensor_elements.get(sensor_element, [])

        if not sensor_values or (max(sensor_values) - min(sensor_values)) / min(sensor_values) >= sensor_threshold:
            return {"status": False, "validator": "STATIC_VALIDATE"}

    result = {"status": True, "validator": "STATIC_VALIDATE"}
    return result


async def protocol_timing_validation(pipeline_config, params, data):
    events = data[pipeline_config["eventsTelemetryData"]["origin"]][
        pipeline_config["eventsTelemetryData"]["name"]
    ]["events"]
    interval_bounds = pipeline_config["interval_bounds"]

    interval_telemetries = {event["name"]: event.get(
        "telemetry", []) for event in events}

    for interval_bound in interval_bounds:
        interval_telemetry = interval_telemetries.get(
            interval_bound["name"], [])
        if not interval_telemetry:
            return {"status": False, "validator": "STATIC_VALIDATE"}
        telemetry_timestamps = list(
            map(lambda x: to_unix_timestamp(x.get("d", "")), interval_telemetry))
        diff_telemetry_timestamp = max(
            telemetry_timestamps) - min(telemetry_timestamps)
        if diff_telemetry_timestamp <= interval_bound["lower_bound"] or diff_telemetry_timestamp >= interval_bound["upper_bound"]:
            return {"status": False, "validator": "STATIC_VALIDATE"}

    result = {"status": True, "validator": "STATIC_VALIDATE"}
    return result

# Data Quality Processors
# static_data_quality
async def unresponsive_sensing_element(pipeline_config, params, data):
    events = data[pipeline_config["eventsTelemetryData"]["origin"]][
        pipeline_config["eventsTelemetryData"]["name"]
    ]["events"]

    telemetries = [
        telemetry.get(telemetry["sn"], {})
        for event in events
        for telemetry in event.get("telemetry", [])
    ]

    if not telemetries:
        return {"status": False, "validator": "STATIC_QUALITY"}

    combined_sensors = {}
    for telemetry in telemetries:
        for sensor in telemetry:
            combined_sensors.setdefault(sensor, []).append(telemetry[sensor])

    for sensor, values in combined_sensors.items():
        if max(values) - min(values) == 0:
            return {"status": False, "validator": "STATIC_QUALITY"}

    result = {"status": True, "validator": "STATIC_QUALITY"}
    return result


async def bme688_reliability(pipeline_config, params, data):
    events = data[pipeline_config["eventsTelemetryData"]["origin"]][
        pipeline_config["eventsTelemetryData"]["name"]
    ]["events"]
    serial_number = data[pipeline_config["serialNumber"]["origin"]][
        pipeline_config["serialNumber"]["name"]
    ]["serialNumbers"][0]
    baseline_created_at = {event["name"]: event["createdAt"] for event in events}

    if "Baseline" not in baseline_created_at:
        return {"status": False, "validator": "STATIC_QUALITY"}
    baseline_created_at = to_datetime(baseline_created_at["Exposure"])

    bme_verification_interval = pipeline_config["bme_verification_interval"]
    bme_calibrations = pipeline_config["bme_calibrations"]

    interval_start = baseline_created_at
    interval_end = update_datetime_by_seconds(
        baseline_created_at, bme_verification_interval)

    telemetries = await _get_telemetry(serial_number, interval_start, interval_end)

    combined_sensor_elements = {
        bme_calibration["name"]: [] for bme_calibration in bme_calibrations}
    for bme_calibration in bme_calibrations:
        sensor_element = bme_calibration["name"]
        sensor_threshold = bme_calibration["threshold"]

        for telemetry in telemetries:
            sensor_values = telemetry.get(telemetry["sn"], {})
            sensor_value = sensor_values.get(sensor_element, 0)
            combined_sensor_elements[sensor_element].append(sensor_value)

        sensor_values = combined_sensor_elements.get(sensor_element, [])

        if not sensor_values or (min(sensor_values) < sensor_threshold):
            return {"status": False, "validator": "STATIC_QUALITY"}

    result = {"status": True, "validator": "STATIC_QUALITY"}
    return result


async def time_sensor_noise_evaluations(pipeline_config, params, data):
    # Retrieve required data from the input
    events = data[pipeline_config["eventsTelemetryData"]["origin"]
                  ][pipeline_config["eventsTelemetryData"]["name"]]["events"]

    # Retrieve noise validation configuration from the pipeline config
    noise_validation_config = pipeline_config.get(
        "noise_validation_config", [])
    sampling_rate_hz = pipeline_config.get("sampling_rate_hz", 1)
    rolling_window_duration = pipeline_config.get(
        "rolling_window_duration", 9)  # Default to 9 seconds
    edge_margin_duration = rolling_window_duration // 2

    rolling_window_size = int(rolling_window_duration * sampling_rate_hz)
    invalid_edge_range = int(edge_margin_duration * sampling_rate_hz)

    for channel_config in noise_validation_config:
        channel_name = channel_config["name"]
        channel_threshold = channel_config["threshold"]
        channel_data = []

        for event in events:
            if "telemetry" in event:
                telemetry_points = event["telemetry"]
                channel_values = [point[point["sn"]].get(
                    channel_name, float('inf')) for point in telemetry_points]
                channel_data.extend(channel_values)

        if len(channel_data) == 0:
            continue

        # Convert the channel data to a NumPy array for faster processing
        channel_data = np.array(channel_data)

        # Apply median filter to the channel data
        med_filtered_data = medfilt(
            channel_data, kernel_size=rolling_window_size)

        # Calculate normalized noise and validate
        valid_data_range = slice(invalid_edge_range, -invalid_edge_range)
        norm_di = (channel_data - med_filtered_data) / med_filtered_data
        max_normalized_noise = np.max(norm_di[valid_data_range])

        if max_normalized_noise > channel_threshold:
            return {"status": False, "validator": "STATIC_QUALITY"}
    result = {"status": True, "validator": "STATIC_QUALITY"}
    return result

async def manage_annotation_verification_status(pipeline_config, params, data):
    annotation_id = params["annotationId"]
    verification_signal = pipeline_config.get("verification_signal", False)
    quality = {}
    validation = {}
    verification_status = ValidationStatus[await get_annotation_validation_status(annotation_id)]

    if verification_signal == "START":
        asyncio.create_task(start_annotation_validation(annotation_id))
        return {"status": True}

    if verification_signal == "STATIC_VALIDATE":
        validation = {processor_name: "Passed" if (processor_results["status"]) else "Failed" 
                                    for processor_name, processor_results in data["pipeline"].items()
                                    if processor_results.get("validator", None) == "STATIC_VALIDATE"}
        validation_status = all(validation.values())
        current_verification_status = ValidationStatus.VALIDATION_CHECK_FAILED if not validation_status else ValidationStatus.IN_PROGRESS

    if verification_signal == "STATIC_QUALITY":
        quality = {processor_name:  "Passed" if (processor_results["status"]) else "Failed" 
                                for processor_name, processor_results in data["pipeline"].items()
                                if processor_results.get("validator", None) == "STATIC_QUALITY"}
        quality_status = all(quality.values())
        current_verification_status = ValidationStatus.QUALITY_CHECK_FAILED if not quality_status else ValidationStatus.IN_PROGRESS

    if verification_signal == "END":
        current_verification_status = ValidationStatus.SUCCESS if verification_status == ValidationStatus.IN_PROGRESS else ValidationStatus.FAILED

    asyncio.create_task(update_annotation_validation_status(annotation_id, current_verification_status, quality_results=quality, validation_results=validation))
    return {"status": True}
