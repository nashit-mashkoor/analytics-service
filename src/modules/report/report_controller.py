import os
import sys
from typing import Optional

from dotenv import load_dotenv
from envs import env
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import ORJSONResponse

from report_dto import AnalyticsRequest, ProcessResponse, Result
from report_service import create, get

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

load_dotenv()

SWAGGER_BASEPATH = env(
    "SWAGGER_BASEPATH", var_type="string", default="/", allow_none=False
)
router = APIRouter(tags=["Report"])


@router.post(f"/{SWAGGER_BASEPATH}/processes", response_model=ProcessResponse)
async def create_process(request: Request, payload: AnalyticsRequest):
    try:
        cid = request.state.cid

        result = await create(payload)
        return ORJSONResponse(
            {"cid": cid, "processId": result.uuid, "status": result.status}
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"creating process failed, {e}",
        )


@router.post(f"/{SWAGGER_BASEPATH}/processes/{'processId'}", response_model=Result)
async def get_process(request: Request, processId: str, cid: Optional[str] = None):
    try:
        cid = cid or request.state.cid
        resutl = await get(cid, processId)
        return ORJSONResponse(resutl)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Process not found, {e}",
        )
