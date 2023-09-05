import re

from envs import env
from datetime import datetime
from pymongo import MongoClient
from singleton_decorator import singleton
from string import Template
from analytics_utils.logging import Logging

logging_instance = Logging()
logger = logging_instance.get_logger()


@singleton
class Database:
    def __init__(self):
        try:
            self.client = MongoClient(
                env(
                    "MONGO_PERSISTENCE_SERVICE_URI", var_type="string", allow_none=False
                )
            )
            self.db = self.client[
                (env("MONGO_DB_NAME", var_type="string", allow_none=False))
            ]
            logger.info(f"connected to databse.")
        except Exception as e:
            logger.error("connecting to database failed")

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def render_mongo_aggregation_object(self, data, replacements):
        if isinstance(data, dict):
            return {key: self.render_mongo_aggregation_object(value, replacements) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.render_mongo_aggregation_object(item, replacements) for item in data]
        elif isinstance(data, str):
            for key, value in replacements.items():
                if "$" + key == data:
                    return value
        else:
            return data
