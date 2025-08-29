import logging
import sys
from typing import Optional
import colorlog
from settings import LOGGING_LEVEL

COLOR_FORMAT = "%(log_color)s%(levelname)s - %(message)s%(reset)s"


class AppLogger:
    _logger: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, name: str = "app") -> logging.Logger:
        if cls._logger is None:
            cls._setup_logger(name)
        return cls._logger

    @classmethod
    def _setup_logger(cls, name: str):
        """Настройка цветного логгера"""
        logger = logging.getLogger(name)
        logger.setLevel(LOGGING_LEVEL)
        logger.handlers.clear()

        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            colorlog.ColoredFormatter(
                COLOR_FORMAT,
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
            )
        )

        logger.addHandler(console_handler)
        logger.propagate = False
        cls._logger = logger


def get_logger(name: str = "app") -> logging.Logger:
    return AppLogger.get_logger(name)
