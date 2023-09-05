import logging

from dotenv import load_dotenv
from envs import env
from pycloudscent import Configurations

load_dotenv()
CONFIGURATION_SERVICE_GRPC_HOST = env(
    "CONFIGURATION_SERVICE_GRPC_HOST", var_type="string", allow_none=False)
CONFIGURATION_SERVICE_GRPC_PORT = env(
    "CONFIGURATION_SERVICE_GRPC_PORT", var_type="string", allow_none=False)


async def get_configuration_by_id(configuration_id):
    config = Configurations(CONFIGURATION_SERVICE_GRPC_HOST,
                            CONFIGURATION_SERVICE_GRPC_PORT)
    result = config.get_configuration(configuration_id)
    return result[0]
