import logging
import sys
from typing import Optional

import colorlog

from settings import LOGGING_LEVEL, SERVICE_NAME

COLOR_FORMAT = (
    f"{SERVICE_NAME}: %(log_color)s%(levelname)s - %(message)s%(reset)s"
)


class AppLogger:
    """Singleton logger class with colored console output configuration."""

    _logger: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, name: str = "app") -> logging.Logger:
        """Retrieves or creates a configured logger instance.

        Args:
            name (str): Name of the logger. Defaults to "app".

        Returns:
            logging.Logger: Configured logger instance with colored output.
        """
        if cls._logger is None:
            cls._setup_logger(name)
        return cls._logger

    @classmethod
    def _setup_logger(cls, name: str):
        """Configures a colored console logger with custom formatting.

        Sets up a logger with colored output, clears existing handlers,
        and configures log levels and formatting.

        Args:
            name (str): Name of the logger to configure.
        """
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
    """Convenience function to retrieve a configured logger instance.

    Args:
        name (str): Name of the logger. Defaults to "app".

    Returns:
        logging.Logger: Configured logger instance from AppLogger.
    """
    return AppLogger.get_logger(name)
