configuration = {
    "cid": "70085cd9-2c96-4362-b1d9-8073cda5afb4",
    "uuid": "e889f794-f7bf-4c21-abae-072e964f6326",
    "name": "analytics",
    "description": "analytics test",
    "clients": "analytics",
    "domains": "analytics",
    "data": {
        "pipeline": [
            {
                "name": "GET_ANNOTATION",
                "function": "get_annotation",
                "requiredParameters": ["annotationId"],
                "optionalParameters": [],
            },
            {
                "name": "GET_EVENT_TELEMETRY",
                "function": "get_event_telemetry",
                "collection": "TelemetryLog",
                "connectionStringName": "MONGO_DATABASE_URL",
                "requiredParameters": [],
                "optionalParameters": [],
                "query": [
                    {
                        "$match": {
                            "sn": "$serialNumbers",
                            "payloadCreateAt": {"$gte": "$fromDate", "$lte": "$toDate"},
                        }
                    },
                    {"$sort": {"payloadCreateAt": 1}},
                ],
                "annotationSerialNumber": {
                    "origin": "pipeline",
                    "name": "GET_ANNOTATION",
                },
                "annotationEvents": {
                    "origin": "pipeline",
                    "name": "GET_ANNOTATION",
                },
            },
            {
                "name": "GENERATE_JSON_FILE",
                "function": "generate_file",
                "fileType": "json",
                "eventsTelemetryData": {
                    "name": "GET_EVENT_TELEMETRY",
                    "origin": "pipeline",
                },
                "annotationId": {
                    "name": "GET_ANNOTATION",
                    "origin": "pipeline",
                },
                "annotationConfigurationId": {
                    "name": "GET_ANNOTATION",
                    "origin": "pipeline",
                },
                "annotationMetadataDetails": {
                    "name": "GET_ANNOTATION",
                    "origin": "pipeline",
                },
                "annotationIdentities": {
                    "name": "GET_ANNOTATION",
                    "origin": "pipeline",
                },
                "annotationCreatedAt": {
                    "name": "GET_ANNOTATION",
                    "origin": "pipeline",
                },
                "serialNumbers": {
                    "name": "GET_ANNOTATION",
                    "origin": "pipeline",
                },
                "requiredParameters": [],
                "optionalParameters": [],
            },
            {
                "name": "GENERATE_CSV_FILE",
                "function": "generate_file",
                "fileType": "csv",
                "eventsTelemetryData": {
                    "name": "GET_EVENT_TELEMETRY",
                    "origin": "pipeline",
                },
                "annotationId": {
                    "name": "GET_ANNOTATION",
                    "origin": "pipeline",
                },
                "annotationConfigurationId": {
                    "name": "GET_ANNOTATION",
                    "origin": "pipeline",
                },
                "annotationMetadataDetails": {
                    "name": "GET_ANNOTATION",
                    "origin": "pipeline",
                },
                "annotationIdentities": {
                    "name": "GET_ANNOTATION",
                    "origin": "pipeline",
                },
                "annotationCreatedAt": {
                    "name": "GET_ANNOTATION",
                    "origin": "pipeline",
                },
                "serialNumbers": {
                    "name": "GET_ANNOTATION",
                    "origin": "pipeline",
                },
                "requiredParameters": [],
                "optionalParameters": [],
            },
            {
                "name": "UPLOAD_CSV_GCP",
                "function": "upload_to_gcp",
                "bucketName": "dv2-analytics-service",
                "path": "annotations",
                "uploadFile": {
                    "name": "GENERATE_CSV_FILE",
                    "origin": "pipeline",
                },
                "annotationCreatedAt": {
                    "name": "GET_ANNOTATION",
                    "origin": "pipeline",
                },
                "requiredParameters": [],
                "optionalParameters": [],
            },
            {
                "name": "UPLOAD_JSON_GCP",
                "function": "upload_to_gcp",
                "bucketName": "dv2-analytics-service",
                "path": "annotations",
                "uploadFile": {
                    "name": "GENERATE_JSON_FILE",
                    "origin": "pipeline",
                },
                "annotationCreatedAt": {
                    "name": "GET_ANNOTATION",
                    "origin": "pipeline",
                },
                "requiredParameters": [],
                "optionalParameters": [],
            },
            {
                "name": "START_ANNOTATION_VERIFICATION",
                "function": "manage_annotation_verification_status",
                "verification_signal": "START",
                "requiredParameters": ["annotationId"],
                "optionalParameters": [],
            },
            {
                "name": "MAX_CONSECUTIVE_DROPPED_PAYLOAD",
                "function": "max_consecutive_dropped_payload",
                "eventsTelemetryData": {
                    "name": "GET_EVENT_TELEMETRY",
                    "origin": "pipeline",
                },
                "sampling_rate": 5,
                "mcdp_threshold": 10,
                "requiredParameters": [],
                "optionalParameters": [],
            },
            {
                "name": "MEDIAN_CONSECUTIVE_TIME_DELTA",
                "function": "median_consecutive_time_delta",
                "eventsTelemetryData": {
                    "name": "GET_EVENT_TELEMETRY",
                    "origin": "pipeline",
                },
                "sampling_rate": 5,
                "mdt_threshold": 10,
                "requiredParameters": [],
                "optionalParameters": [],
            },
            {
                "name": "MIN_SESSION_COMPLETENESS",
                "function": "min_session_completeness",
                "eventsTelemetryData": {
                    "name": "GET_EVENT_TELEMETRY",
                    "origin": "pipeline",
                },
                "sampling_rate": 5,
                "msc_threshold": 10,
                "requiredParameters": [],
                "optionalParameters": [],
            },
            {
                "name": "STIMULUS_INTERVAL_CONNECTIVITY_VERIFICATION",
                "function": "interval_connectivity_verification",
                "eventsTelemetryData": {
                    "name": "GET_EVENT_TELEMETRY",
                    "origin": "pipeline",
                },
                "interval_names": ["Baseline", "Exposure"],
                "maxdt_threshold": 10,
                "large_gaps_threshold_interval": 10,
                "acceptable_num_gaps_interval": 10,
                "percentage_available_interval": 10,
                "sampling_rate": 10,
                "requiredParameters": [],
                "optionalParameters": [],
            },
            {
                "name": "RECOVERY_INTERVAL_CONNECTIVITY_VERIFICATION",
                "function": "interval_connectivity_verification",
                "eventsTelemetryData": {
                    "name": "GET_EVENT_TELEMETRY",
                    "origin": "pipeline",
                },
                "interval_names": ["Recovery"],
                "maxdt_threshold": 10,
                "large_gaps_threshold_interval": 10,
                "acceptable_num_gaps_interval": 10,
                "percentage_available_interval": 10,
                "sampling_rate": 10,
                "requiredParameters": [],
                "optionalParameters": [],
            },
            {
                "name": "STABILITY_OF_REFERENCE_SENSING_ELEMENTS",
                "function": "stability_of_reference_sensing_elements",
                "eventsTelemetryData": {
                    "name": "GET_EVENT_TELEMETRY",
                    "origin": "pipeline",
                },
                "serialNumber": {
                    "origin": "pipeline",
                    "name": "GET_ANNOTATION",
                },
                "verification_interval_seconds": -10,
                "reference_sensing_elements": [
                    {
                        "name": "RRF0",
                        "threshold": 12
                    }
                ],
                "requiredParameters": [],
                "optionalParameters": [],
            },
            {
                "name": "PROTOCOL_TIMING_VALIDATION",
                "function": "protocol_timing_validation",
                "eventsTelemetryData": {
                    "name": "GET_EVENT_TELEMETRY",
                    "origin": "pipeline",
                },
                "interval_bounds": [
                    {
                        "name": "Baseline",
                        "lower_bound": 100000,
                        "upper_bound": 12
                    }
                ],
                "requiredParameters": [],
                "optionalParameters": [],
            },
            {
                "name": "VALIDATION_ANNOTATION_VERIFICATION",
                "function": "manage_annotation_verification_status",
                "verification_signal": "STATIC_VALIDATE",
                "requiredParameters": ["annotationId"],
                "optionalParameters": [],
            },
            {
                "name": "UNRESPONSIVE_SENSING_ELEMENT",
                "function": "unresponsive_sensing_element",
                "eventsTelemetryData": {
                    "name": "GET_EVENT_TELEMETRY",
                    "origin": "pipeline",
                },
                "requiredParameters": [],
                "optionalParameters": [],
            },
            {
                "name": "BME688_RELIABILITY",
                "function": "bme688_reliability",
                "eventsTelemetryData": {
                    "name": "GET_EVENT_TELEMETRY",
                    "origin": "pipeline",
                },
                "serialNumber": {
                    "origin": "pipeline",
                    "name": "GET_ANNOTATION",
                },
                "bme_verification_interval":   10,
                "bme_calibrations": [
                    {
                        "name": "IAQ0",
                        "threshold": 123
                    }
                ],
                "large_gaps_threshold_interval": 10,
                "acceptable_num_gaps_interval": 10,
                "percentage_available_interval": 10,
                "sampling_rate": 10,
                "requiredParameters": [],
                "optionalParameters": [],
            },
            {
                "name": "TIME_SENSOR_NOISE_EVALUATIONS",
                "function": "time_sensor_noise_evaluations",
                "eventsTelemetryData": {
                    "name": "GET_EVENT_TELEMETRY",
                    "origin": "pipeline",
                },
                "sampling_rate_hz": 1,
                "rolling_window_duration": 9,
                "noise_validation_config": [
                    {
                        "name": "CHR0",
                        "threshold": 123
                    }
                ],
                "requiredParameters": [],
                "optionalParameters": [],
            },
            {
                "name": "QUALITY_ANNOTATION_VERIFICATION",
                "function": "manage_annotation_verification_status",
                "verification_signal": "STATIC_QUALITY",
                "requiredParameters": ["annotationId"],
                "optionalParameters": [],
            },
            {
                "name": "END_ANNOTATION_VERIFICATION",
                "function": "manage_annotation_verification_status",
                "verification_signal": "END",
                "requiredParameters": ["annotationId"],
                "optionalParameters": [],
            }
        ],
    },
    "type": "ANALYTICS",
    "status": "PUBLISHED",
    "version": 1,
    "createdAt": "2023-04-14T17:57:49.329Z",
    "createdBy": "60755901-045e-42a5-b225-1f79a24f04a4",
    "updatedAt": "2023-04-14T18:00:38.854Z",
    "updatedBy": "60755901-045e-42a5-b225-1f79a24f04a4",
}
