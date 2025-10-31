import json
import logging
import sys
from datetime import datetime
from typing import Deque, Any, Optional
from collections import deque
import asyncio

from settings import settings


log_queue: Deque[dict[str, Any]] = deque()
log_queue_task: Optional[asyncio.Task] = None


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

        log_queue.append(log_entry)

        return json.dumps(log_entry)


async def start_log_processing():
    global log_queue_task
    if log_queue_task is None:
        log_queue_task = asyncio.create_task(_process_log_queue())


async def stop_log_processing():
    global log_queue_task
    if log_queue_task:
        log_queue_task.cancel()
        try:
            await log_queue_task
        except asyncio.CancelledError:
            pass
        log_queue_task = None


async def _process_log_queue():
    from services.kafka_logger_producer import kafka_logger_producer

    while True:
        try:
            if log_queue:
                log_data = log_queue.popleft()
                await kafka_logger_producer.send_log(log_data)
            else:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(0.1)


def get_logger(name: str = "app") -> logging.Logger:
    return AppLogger.get_logger(name)
