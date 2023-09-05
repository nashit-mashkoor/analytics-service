import json
import logging
import sys
import threading
import time
import uuid

from dotenv import load_dotenv
from envs import env
from singleton_decorator import singleton

load_dotenv()


class LoggingException(Exception):
    pass


@singleton
class Logging:
    def __init__(self) -> None:
        self.logger = logging.getLogger("analytics-ingest-service")
        log_level = env(
            "LOG_LEVEL", var_type="string", default="INFO", allow_none=False
        )

        self.logger.setLevel(level=log_level)
        handler = JsonStreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        self.logger.addHandler(handler)

    def get_logger(self):
        return self.logger

    @staticmethod
    def inject_logger(cls):
        log = Logging()
        logger = log.get_logger()
        cls.logger = logger
        return cls


class JsonFormatter(logging.Formatter):
    def __init__(self):
        super(JsonFormatter, self).__init__()

    def format(self, record):
        cid = getattr(record, "cid", str(uuid.uuid4()))
        log = {
            "written_at": time.strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime(record.created)
            ),
            "written_ts": record.created * 1e9,
            "msg": record.getMessage(),
            "type": "log",
            "logger": record.name,
            "thread": threading.current_thread().name,
            "level": record.levelname,
            "module": record.module,
            "line_no": record.lineno,
            "cid": cid,
        }
        # add method and URL information if present
        if hasattr(record, "method"):
            log["method"] = record.method
        if hasattr(record, "url"):
            log["url"] = record.url

        return json.dumps(log)


class JsonStreamHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        super(JsonStreamHandler, self).__init__(stream)
        self.formatter = JsonFormatter()

    def emit(self, record):
        try:
            log = json.loads(self.formatter.format(record))
            self.stream.write(json.dumps(log) + "\n")
            self.flush()
        except Exception:
            self.handleError(record)
