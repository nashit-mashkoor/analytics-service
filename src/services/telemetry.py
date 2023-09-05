import io
import csv

CSV_HEADER = [
    "component_sn",
    "product_sn",
    "event_name",
    "annotation_id",
    "configuration_id",
    "pui",
    "participant_group",
    "participant_details",
    "metadata",
    "payloadCreateAt",
    "event",
]

def __create_telemetry_rows(annotationId, annotationConfigurationId,
                            annotationMetadataDetails, annotationIdentities,
                            event, metric):
    rows = []
    for telemetry_sn in metric["tsns"]:
        event_data = {
            key: value for key, value in event.items() if key != "telemetry"
        }
        participant = [
            (i) for i in annotationIdentities if i["type"] == "PARTICIPANT"
        ][0]

        sensorData = list(metric[telemetry_sn].values())

        data_rows = [
            metric["tsns"][0],
            metric["sn"],
            event_data["name"],
            annotationId,
            annotationConfigurationId,
            participant["reference"],
            participant["metadata"].get("group"),
            participant["metadata"].get("details"),
            annotationMetadataDetails,
            metric["payloadCreateAt"],
            event_data,
        ]

        data_rows[5:5] = sensorData
        data_rows_modified = [
            "None" if item is None else item for item in data_rows
        ]

        rows.append(data_rows_modified)

    return rows

def __map_values_to_csv_header(annotationId, annotationConfigurationId,
                            annotationMetadataDetails, annotationIdentities, event):
    rows = []
    if "telemetry" not in event:
        return
    if len(event["telemetry"]) == 0:
        return
    for metric in event["telemetry"]:
        telemetry_rows = __create_telemetry_rows(
                                                annotationId, annotationConfigurationId,
                                                annotationMetadataDetails, annotationIdentities,
                                                event, metric)
        rows.extend(telemetry_rows)
    return rows

def to_csv(annotationId, annotationConfigurationId, 
            annotationMetadataDetails, annotationIdentities, events):
    output = io.StringIO()
    writer = csv.writer(output)
    telemetry_headers = []
    if len(events[0]["telemetry"]) == 0:
        return None

    for tsns in events[0]["telemetry"][0]["tsns"]:
        telemetry_headers.extend(events[0]["telemetry"][0][tsns])

    CSV_HEADER[5:5] = telemetry_headers

    writer.writerow(CSV_HEADER)
    rows = []
    for event in events:
        event_rows = __map_values_to_csv_header(annotationId, annotationConfigurationId,
                                                annotationMetadataDetails, annotationIdentities, event)
        if event_rows is not None:
            rows.extend(event_rows)
    if len(rows) == 0:
        return None

    writer.writerows(rows)
    csv_data = output.getvalue()
    output.close()
    return csv_data