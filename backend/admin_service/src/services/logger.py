import asyncio
import json
import logging
import sys
from datetime import datetime

from services.kafka_logger_producer import kafka_logger_producer
from settings import settings


class AppLogger:
    @classmethod
    def get_logger(cls, name: str = "app") -> logging.Logger:
        return cls._setup_logger(name)

    @classmethod
    def _setup_logger(cls, name: str):
        logger = logging.getLogger(name)
        logger.setLevel(settings.LOGGING_LEVEL)
        logger.handlers.clear()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())

        logger.addHandler(console_handler)
        logger.propagate = False
        return logger


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "service": settings.SERVICE_NAME,
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        asyncio.create_task(self._send_to_kafka(log_entry))

        return json.dumps(log_entry)

    async def _send_to_kafka(self, log_data: dict):
        try:
            await kafka_logger_producer.send_log(log_data)
        except Exception:
            pass


def get_logger(name: str = "app") -> logging.Logger:
    return AppLogger.get_logger(name)
