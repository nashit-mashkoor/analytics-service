import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from dotenv import load_dotenv
from envs import env
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from utilities_dto import HealthDto, PeripheryDto

load_dotenv()

router = APIRouter()

SWAGGER_BASEPATH = env(
    "SWAGGER_BASEPATH", var_type="string", default="/", allow_none=False
)
router = APIRouter(tags=["utilities"])


@router.get(f"/{SWAGGER_BASEPATH}/rest/v1/utilities/health", response_model=HealthDto)
def health_check():
    return ORJSONResponse({"status": "ok"})


@router.get(
    f"/{SWAGGER_BASEPATH}/rest/v1/utilities/periphery",
    response_model=PeripheryDto,
)
def periphery_check():
    return ORJSONResponse({"status": "OK", "dependencies": []})
