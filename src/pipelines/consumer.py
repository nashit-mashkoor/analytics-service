import asyncio

async def consumer(queue, pipeline_result):
    while True:
        item = await queue.get()
        if item is None:
            break
    await process_validation_result(pipeline_result)
    return pipeline_result

async def process_validation_result(pipeline_result):
    if pipeline_result is None or pipeline_result.get("validationPipeline", {}) == {}:
        return
    ## To Do
    ## Summarise the result and hit the neccsary web api
