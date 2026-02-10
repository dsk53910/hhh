"""
Utilities package for HHH Bot
"""

from .logger import (
    get_logger,
    setup_logging,
    LoggerMixin,
    log_function_call,
    log_async_function_call,
)
from .helpers import (
    generate_hash,
    sanitize_text,
    truncate_text,
    format_salary,
    format_experience,
    format_employment,
    format_schedule,
    parse_keywords,
    is_valid_vacancy_url,
    extract_vacancy_id_from_url,
    get_current_time,
    retry_async,
    chunk_list,
    safe_get_nested,
    format_datetime,
)

__all__ = [
    # Logger utilities
    "get_logger",
    "setup_logging",
    "LoggerMixin",
    "log_function_call",
    "log_async_function_call",
    # Helper utilities
    "generate_hash",
    "sanitize_text",
    "truncate_text",
    "format_salary",
    "format_experience",
    "format_employment",
    "format_schedule",
    "parse_keywords",
    "is_valid_vacancy_url",
    "extract_vacancy_id_from_url",
    "get_current_time",
    "retry_async",
    "chunk_list",
    "safe_get_nested",
    "format_datetime",
]
