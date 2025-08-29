import logging
import sys
from typing import Optional

from settings import LOGGING_LEVEL

LOG_FORMAT = "%(levelname)s - %(message)s"


class AppLogger:
    _logger: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, name: str = "app") -> logging.Logger:
        if cls._logger is None:
            cls._setup_logger(name)
        return cls._logger

    @classmethod
    def _setup_logger(cls, name: str):
        """Настройка логгера"""
        logger = logging.getLogger(name)
        logger.setLevel(LOGGING_LEVEL)

        logger.handlers.clear()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(LOG_FORMAT)
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.propagate = False

        cls._logger = logger


def get_logger(name: str = "app") -> logging.Logger:
    return AppLogger.get_logger(name)
