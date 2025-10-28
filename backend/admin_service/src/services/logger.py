"""Logging configuration for microservices with Elasticsearch integration.

This module provides structured JSON logging with asynchronous Elasticsearch
integration to avoid blocking FastAPI request handlers.

Example:
    >>> from services.logger import get_logger
    >>> logger = get_logger("my_service")
    >>> logger.info("Service started", extra={"port": 8000})

Attributes:
    ElasticsearchHandler: Async log handler for Elasticsearch integration.
    AppLogger: Factory class for creating configured loggers.
    JSONFormatter: Formatter for structured JSON log output.
"""

import logging
import sys
import json
import asyncio
import concurrent.futures
from datetime import datetime
from typing import Optional, Dict, Any
from elasticsearch import AsyncElasticsearch
from settings import settings


class ElasticsearchHandler(logging.Handler):
    """Asynchronous log handler for Elasticsearch integration.

    This handler uses thread pool to send logs to Elasticsearch without blocking
    the main application thread.

    Attributes:
        es: Async Elasticsearch client instance.
        _thread_pool: Thread pool for async log processing.
    """

    _instance: Optional["ElasticsearchHandler"] = None
    _initialized: bool = False

    def __new__(cls):
        """Creates singleton instance of ElasticsearchHandler.

        Returns:
            ElasticsearchHandler: Singleton instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initializes the Elasticsearch handler with async client and thread pool."""
        if not self._initialized:
            super().__init__()
            self.es: AsyncElasticsearch = AsyncElasticsearch(
                ["http://elasticsearch:9200"],
                request_timeout=30,
                max_retries=3,
                retry_on_timeout=True,
            )
            self._thread_pool: concurrent.futures.ThreadPoolExecutor = (
                concurrent.futures.ThreadPoolExecutor(max_workers=1)
            )
            self._initialized = True

    def emit(self, record: logging.LogRecord) -> None:
        """Adds a log record to the processing queue.

        Args:
            record: Log record to process and send to Elasticsearch.
        """
        try:
            log_entry = json.loads(self.format(record))
            # Non-blocking submission to thread pool
            self._thread_pool.submit(self._send_log_sync, log_entry)
        except Exception as e:
            print(f"Failed to queue log entry: {e}", file=sys.stderr)

    def _send_log_sync(self, log_entry: Dict[str, Any]) -> None:
        """Synchronous wrapper for async log sending.
        
        Args:
            log_entry: Structured log data to send.
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._send_to_elasticsearch(log_entry))
        except Exception as e:
            print(f"Failed to send log to Elasticsearch: {e}", file=sys.stderr)
        finally:
            if loop and not loop.is_closed():
                loop.close()

    async def _send_to_elasticsearch(self, log_entry: Dict[str, Any]) -> None:
        """Sends a log entry to Elasticsearch.

        Args:
            log_entry: Structured log data to send.
        """
        try:
            await self.es.index(
                index=(
                    f"microservices-{settings.SERVICE_NAME.lower()}-"
                    f"{datetime.now().strftime('%Y.%m.%d')}"
                ),
                body=log_entry,
            )
        except Exception as e:
            print(f"Elasticsearch indexing error: {e}", file=sys.stderr)

    async def close(self) -> None:
        """Closes the Elasticsearch client and thread pool."""
        if self.es:
            await self.es.close()
        self._thread_pool.shutdown(wait=True)


class AppLogger:
    """Factory class for creating configured logger instances.

    Attributes:
        _es_handler: Shared Elasticsearch handler instance.
    """

    _es_handler: Optional[ElasticsearchHandler] = None

    @classmethod
    def get_logger(cls, name: str = "app") -> logging.Logger:
        """Creates and returns a configured logger instance.

        Args:
            name: Logger name. Defaults to "app".

        Returns:
            logging.Logger: Configured logger instance.
        """
        return cls._setup_logger(name)

    @classmethod
    def _setup_logger(cls, name: str) -> logging.Logger:
        """Configures a logger with console and Elasticsearch handlers.

        Args:
            name: Name of the logger to configure.

        Returns:
            logging.Logger: Configured logger instance.
        """
        logger = logging.getLogger(name)
        logger.setLevel(settings.LOGGING_LEVEL)
        logger.handlers.clear()

        # Console handler for local development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        logger.addHandler(console_handler)

        # Elasticsearch handler for production logging
        if cls._es_handler is None:
            cls._es_handler = ElasticsearchHandler()
            cls._es_handler.setFormatter(JSONFormatter())

        logger.addHandler(cls._es_handler)
        logger.propagate = False
        return logger

    @classmethod
    async def close_elasticsearch(cls) -> None:
        """Closes the shared Elasticsearch handler connection.

        This should be called during application shutdown.
        """
        if cls._es_handler:
            await cls._es_handler.close()


class JSONFormatter(logging.Formatter):
    """Formatter for structured JSON log output."""

    def format(self, record: logging.LogRecord) -> str:
        """Formats a log record as JSON string.

        Args:
            record: Log record to format.

        Returns:
            str: JSON string representation of the log record.
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

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def get_logger(name: str = "app") -> logging.Logger:
    """Creates and returns a configured logger instance.

    This is the main entry point for getting logger instances.

    Args:
        name: Logger name. Defaults to "app".

    Returns:
        logging.Logger: Configured logger instance.
    """
    return AppLogger.get_logger(name)


async def close_logging() -> None:
    """Closes logging resources.

    This should be called during application shutdown to ensure
    proper cleanup of Elasticsearch connections.
    """
    await AppLogger.close_elasticsearch()
