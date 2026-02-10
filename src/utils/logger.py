"""
Logging configuration for HHH Bot
Provides structured logging with correlation IDs and proper formatting
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = False,
) -> None:
    """
    Configure logging for the application

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        json_format: Whether to use JSON formatted logs
    """

    # Remove existing handlers
    logging.getLogger().handlers.clear()

    # Create formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Configure handlers
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    # Apply formatter to handlers
    for handler in handlers:
        handler.setFormatter(formatter)
        handler.setLevel(getattr(logging, log_level.upper()))

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
    )

    # Set specific logger levels
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return get_logger(self.__class__.__name__)


def log_function_call(func):
    """Decorator to log function entry and exit"""

    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)

        logger.debug(
            "function_call: %s, args: %d, kwargs: %s",
            func.__name__,
            len(args),
            list(kwargs.keys()),
        )

        try:
            result = func(*args, **kwargs)
            logger.debug(
                "function_success: %s, result_type: %s",
                func.__name__,
                type(result).__name__,
            )
            return result
        except Exception as e:
            logger.error(
                "function_error: %s, error: %s",
                func.__name__,
                str(e),
                exc_info=True,
            )
            raise

    return wrapper


def log_async_function_call(func):
    """Decorator to log async function entry and exit"""

    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)

        logger.debug(
            "async_function_call: %s, args: %d, kwargs: %s",
            func.__name__,
            len(args),
            list(kwargs.keys()),
        )

        try:
            result = await func(*args, **kwargs)
            logger.debug(
                "async_function_success: %s, result_type: %s",
                func.__name__,
                type(result).__name__,
            )
            return result
        except Exception as e:
            logger.error(
                "async_function_error: %s, error: %s",
                func.__name__,
                str(e),
                exc_info=True,
            )
            raise

    return wrapper
