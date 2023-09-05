import asyncio
import json

from consumer import consumer
from datetime import datetime
from modules.report.report_dto import STATUS
from pipelines.pipeline_exception import PipelineExceptions
from producer import producer
from services.database import Database
from analytics_utils.logging import Logging

logging_instance = Logging()

def run_pipeline(configuration, payload, uuid):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(pipeline(configuration, payload, uuid))

async def pipeline(configuration, payload, uuid):
    logger = logging_instance.get_logger()
    logger.debug(
        {
            "msg": f"Starting pipeline for process id: {uuid}"
        }
    )
    start_time = datetime.utcnow()
    pipeline_result = {}
    queue = asyncio.Queue()
    process_result = {}
    data_base = Database()
    try:
        result = await asyncio.gather(
            producer(configuration, queue, payload, pipeline_result),
            consumer(queue, pipeline_result),
        )

        process_result = json.dumps(result[-1], default=str)
        end_time = datetime.utcnow()
        process_time = (end_time - start_time).total_seconds()
        data_base.update_process(
            uuid, process_time, STATUS.COMPLETE.value, process_result
        )
        logger.debug(
            {
                "msg": f"Pipeline for process id: {uuid} done"
            }
        )
        return process_result
    except Exception as e:
        end_time = datetime.utcnow()
        process_time = (end_time - start_time).total_seconds() * 1000
        process_result = {
            "configurationId": f"{payload.configurationId}",
            "msg": "failed to run  pipeline queue",
        }
        data_base.update_process(
            uuid, process_time, STATUS.FAILED.value, process_result
        )

        logger.debug(
            {
                "configurationId": f"{payload.configurationId}",
                "msg": "failed to run  pipeline queue",
            }
        )
        raise PipelineExceptions("failed to run  pipeline queue")
