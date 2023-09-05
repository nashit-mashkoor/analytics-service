import threading
from mock_data.configurations import configuration as default_config
from pipelines.pipeline import run_pipeline
from report_dto import AnalyticsRequest
from services.database import Database
from services.configuration import get_configuration_by_id

async def create(payload: AnalyticsRequest):
    data_base = Database()
    config_id = payload.configurationId
    configuration = await get_configuration_by_id(config_id) if config_id else default_config
    process = data_base.create_process(payload, configuration["version"])
    # Create and start the background thread
    background_thread = threading.Thread(target=lambda: run_pipeline(configuration, payload, process.uuid))
    background_thread.daemon = True  # This allows the thread to exit when the main program exits
    background_thread.start()

    return process


async def get(cid: str, uuid):
    data_base = Database()
    process = data_base.get_process(uuid, cid)
    return process
