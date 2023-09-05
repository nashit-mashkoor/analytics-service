import logging
import os
import sys

from dotenv import load_dotenv
from envs import env
from fastapi import APIRouter, FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse
from modules.report import report_controller
from modules.utilities import utilities_controller
from services import models
from services.database import engine
from services.mongodb.database import Database
from starlette_prometheus import PrometheusMiddleware, metrics
from analytics_utils.logging import Logging
from analytics_utils.middlewares import LogRequestsMiddleware

models.Base.metadata.create_all(bind=engine)

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

load_dotenv()

router = APIRouter()

SWAGGER_BASEPATH = env(
    "SWAGGER_BASEPATH", var_type="string", default="/", allow_none=False
)

app = FastAPI(
    root_path=f"/{SWAGGER_BASEPATH}",
    title="Analytics Service",
    description="The purpose of the service is to provide an easy interface to metrics needed for various "
    "client applications",
    version="1.0",
    default_response_class=ORJSONResponse,
    servers=[
        {
            "url": "/",
            "description": "local-deployment"
        }
    ],
    openapi_url="/openapi.json",
    docs_url="/rest/v1/docs"
)

logging.getLogger("uvicorn.error").setLevel(logging.FATAL)
logging.getLogger("uvicorn.access").setLevel(logging.FATAL)
logging_instance = Logging()
logger = logging_instance.get_logger()


app.add_middleware(PrometheusMiddleware)
app.add_middleware(LogRequestsMiddleware)

app.add_api_route(f"/{SWAGGER_BASEPATH}/rest/v1/utilities/metrics", metrics)

app.include_router(utilities_controller.router)
app.include_router(report_controller.router)


@app.on_event("startup")
async def startup_event():
    logger.info("application started.")
    Database()
