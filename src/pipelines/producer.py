import asyncio
import pipelines

from analytics_utils.logging import Logging
from pipelines.pipeline_exception import PipelineExceptions

logging_instance = Logging()
logger = logging_instance.get_logger()

async def producer(configuration, queue, payload, data):
    data["pipeline"] = {}
    for pipeline_config in configuration["data"]["pipeline"]:
        params = {}
        if any(
            param not in payload.params
            for param in pipeline_config["requiredParameters"]
        ):
            raise Exception(
                f'required parameter {pipeline_config["requiredParameters"]} was not provided',
            )

        params = {
            param["param"]: param["value"]
            for param in pipeline_config["optionalParameters"]
        }
        if payload.params:
            params.update(
                payload.params
            )  # this will overwrite values for duplicate keys in optionalParameters

        try:
            logger.debug(
                {
                    "msg": f"Running pipeline step: {pipeline_config['function']}"
                }
            )
            pipeline_step_result = await pipelines.__dict__[
                pipeline_config["function"]
            ](pipeline_config, params, data)
            data["pipeline"][pipeline_config["name"]] = pipeline_step_result
            await queue.put(pipeline_step_result)
        except Exception as e:
            logger.debug(
                {
                    "pipeline_config": f"{pipeline_config}",
                    "params": f"{params}",
                    "function": f"{ pipeline_config['function']}",
                    "data": data,
                }
            )
            raise PipelineExceptions(f"Failed in executing pipeline functions: { pipeline_config['function']}")

    await queue.put(None)
