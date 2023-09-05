import requests
from dotenv import load_dotenv
from envs import env
from enum import Enum
from services.sso import SSO
from analytics_utils.logging import Logging

load_dotenv()
ANNOTATION_SERVICE_BASE_PATH = env(
    "ANNOTATION_SERVICE_BASE_PATH", var_type="string", allow_none=False
)

logger = Logging().get_logger()


class ValidationStatus(Enum):
    SUCCESS = 'SUCCESS'
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    QUALITY_CHECK_FAILED = 'QUALITY_CHECK_FAILED'
    FAILED = 'FAILED'
    VALIDATION_CHECK_FAILED = 'VALIDATION_CHECK_FAILED'


class AnnotationServiceExceptions(Exception):
    pass


def __build_headers():
    try:
        sso = SSO()
        token = sso.get_token()["access_token"]
        headers = {"accept": "application/json", "Authorization": f"Bearer {token}"}
        return headers
    except Exception as e:
        logger.error("Cant create headers", e)


async def get_annotations_by_id(annotation_id):
    try:
        path = f"{ANNOTATION_SERVICE_BASE_PATH}/client/annotations/{annotation_id}"
        response = requests.get(path, timeout=120, headers=__build_headers())
        response.raise_for_status()  # raises an exception for non-2xx status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Request error:", e)
        raise AnnotationServiceExceptions(e)


async def start_annotation_validation(annotation_id):
    try:
        path = f"{ANNOTATION_SERVICE_BASE_PATH}/client/validations/{annotation_id}/validations/start"
        response = requests.post(path, timeout=120, headers=__build_headers())
        response.raise_for_status()  # raises an exception for non-2xx status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Request error:", e)
        raise AnnotationServiceExceptions(e)


async def get_annotation_validation_status(annotation_id):
    try:
        path = f"{ANNOTATION_SERVICE_BASE_PATH}/client/validations/{annotation_id}/validations/status"
        response = requests.get(path, timeout=120, headers=__build_headers())
        response.raise_for_status()  # raises an exception for non-2xx status codes
        return response.json()["validationStatus"]
    except requests.exceptions.RequestException as e:
        logger.error("Request error:", e)
        raise AnnotationServiceExceptions(e)


async def update_annotation_validation_status(annotation_id, validation_status, quality_results=None, validation_results=None):
    try:
        path = f"{ANNOTATION_SERVICE_BASE_PATH}/client/validations/{annotation_id}/validations/status"
        headers = __build_headers()
        payload = {
            "validationStatus": validation_status.value,
            "validationResult": {
                "quality": quality_results if quality_results else {},
                "validation": validation_results if validation_results else {}
            }

        }
        response = requests.patch(
            path, json=payload, timeout=120, headers=headers)
        response.raise_for_status()  # raises an exception for non-2xx status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Request error:", e)
        raise AnnotationServiceExceptions(e)
