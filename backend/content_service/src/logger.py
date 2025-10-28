import logging
import sys
import json
from datetime import datetime

from settings import settings


class AppLogger:
    @classmethod
    def get_logger(cls, name: str = "app") -> logging.Logger:
        return cls._setup_logger(name)

    @classmethod
    def _setup_logger(cls, name: str):
        logger = logging.getLogger(name)
        logger.setLevel(settings.LOG_LEVEL)
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
        return json.dumps(log_entry)


def get_logger(name: str = "app") -> logging.Logger:
    return AppLogger.get_logger(name)
