import json
import logging
import sys
from datetime import datetime

from settings import settings


class AppLogger:
    """A utility class for configuring and retrieving application loggers.

    This class provides methods to create and configure logger instances
    with consistent settings across the application.

    Methods:
        get_logger: Retrieves a configured logger instance with the specified name.
    """

    @classmethod
    def get_logger(cls, name: str = "app") -> logging.Logger:
        """Retrieves a configured logger instance.

        Args:
            name: A string representing the name of the logger. Defaults to "app".

        Returns:
            logging.Logger: A configured logger instance with the specified name.

        Note:
            This method relies on the private _setup_logger method for actual
            logger configuration.
        """
        return cls._setup_logger(name)

    @classmethod
    def _setup_logger(cls, name: str):
        """Configures and returns a logger with JSON formatting.

        Sets up a logger with the specified name, configures it to use a JSON
        formatted console handler, and applies application-specific settings.

        Args:
            name: A string representing the name of the logger to configure.

        Returns:
            logging.Logger: A configured logger instance with JSON formatting
            and the specified name.

        Note:
            - Clears any existing handlers from the logger before adding new ones
            - Uses LOG_LEVEL from application settings
            - Disables propagation to prevent duplicate log messages
            - Outputs logs to stdout with JSON formatting
        """
        logger = logging.getLogger(name)
        logger.setLevel(settings.LOG_LEVEL)
        logger.handlers.clear()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())

        logger.addHandler(console_handler)
        logger.propagate = False
        return logger


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging.

    Formats log records as JSON strings with standardized fields for
    better parsing and analysis in log management systems.

    Methods:
        format: Converts a log record into a JSON formatted string.
    """

    def format(self, record):
        """Formats a log record as a JSON string.

        Creates a structured dictionary with standardized fields from the
        log record and converts it to a JSON string.

        Args:
            record: The LogRecord object to be formatted.

        Returns:
            str: A JSON string containing the structured log data with
            the following fields:
                - timestamp: ISO 8601 formatted UTC time
                - service: Service name from application settings
                - logger: Name of the logger that generated the record
                - level: Log level name (e.g., 'INFO', 'ERROR')
                - message: Formatted log message
                - module: Module name where the log was generated
                - function: Function name where the log was generated
                - line: Line number where the log was generated
        """
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
    """Retrieves a configured application logger instance.

    This is a convenience function that provides easy access to the
    application's logging system through the AppLogger class.

    Args:
        name: A string representing the name of the logger. Defaults to "app".

    Returns:
        logging.Logger: A configured logger instance with the specified name.
    """
    return AppLogger.get_logger(name)
