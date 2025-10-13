import logging
import sys

import colorlog

from settings import settings

COLOR_FORMAT = (
    "API Gateway: [%(name)s] "
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s%(reset)s"
)


class AppLogger:
    """Class for creating separate logger instances with customized logging."""

    @classmethod
    def get_logger(cls, name: str = "app") -> logging.Logger:
        """Creates and returns a new logger instance each time it's called.

        Args:
            name (str): Name of the logger. Defaults to "app".

        Returns:
            logging.Logger: Newly created logger instance with proper configuration.

        """
        return cls._setup_logger(name)

    @classmethod
    def _setup_logger(cls, name: str):
        """Sets up a new logger instance with specific configurations.

        Args:
            name (str): The name of the logger being set up.

        Returns:
            logging.Logger: A newly initialized logger object.

        """
        logger = logging.getLogger(name)
        logger.setLevel(settings.LOG_LEVEL)
        logger.handlers.clear()

        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            colorlog.ColoredFormatter(
                COLOR_FORMAT,
                datefmt="%Y-%m-%d %H:%M:%S",
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
        return logger


def get_logger(name: str = "app") -> logging.Logger:
    """Utility method to create and obtain a new logger instance.

    Args:
        name (str): Name of the logger. Defaults to "app".

    Returns:
        logging.Logger: Newly created logger instance via AppLogger.

    """
    return AppLogger.get_logger(name)
