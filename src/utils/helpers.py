"""
Helper utilities and common functions for HHH Bot
"""

import asyncio
import hashlib
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
from functools import wraps
import unicodedata


def generate_hash(text: str, algorithm: str = "md5") -> str:
    """
    Generate hash from text using specified algorithm

    Args:
        text: Text to hash
        algorithm: Hash algorithm (md5, sha1, sha256)

    Returns:
        Hex digest of the hash
    """
    hash_func = getattr(hashlib, algorithm.lower())()
    hash_func.update(text.encode("utf-8"))
    return hash_func.hexdigest()


def sanitize_text(text: str) -> str:
    """
    Sanitize text by removing special characters and normalizing

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text
    """
    # Normalize Unicode characters
    text = unicodedata.normalize("NFKD", text)

    # Remove non-printable characters except newlines and tabs
    text = re.sub(r'[^\w\s\n\t.,!?;:()[\]{}"\'-]', "", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def format_salary(salary: Optional[Dict[str, Any]]) -> str:
    """
    Format salary information from hh.ru API response

    Args:
        salary: Salary dictionary from API

    Returns:
        Formatted salary string
    """
    if not salary:
        return "Зарплата не указана"

    currency = salary.get("currency", "RUR")
    from_amount = salary.get("from")
    to_amount = salary.get("to")

    currency_map = {
        "RUR": "₽",
        "USD": "$",
        "EUR": "€",
    }
    symbol = currency_map.get(currency, currency)

    if from_amount and to_amount:
        return f"{from_amount:,} - {to_amount:,} {symbol}"
    elif from_amount:
        return f"от {from_amount:,} {symbol}"
    elif to_amount:
        return f"до {to_amount:,} {symbol}"
    else:
        return f"Зарплата не указана"


def format_experience(experience: Optional[str]) -> str:
    """
    Format experience requirements

    Args:
        experience: Experience string from API

    Returns:
        Formatted experience string
    """
    experience_map = {
        "noExperience": "Без опыта",
        "between1And3": "1-3 года",
        "between3And6": "3-6 лет",
        "moreThan6": "Более 6 лет",
    }

    return experience_map.get(experience, "Не указано") if experience else "Не указано"


def format_employment(employment_list: List[Dict[str, Any]]) -> str:
    """
    Format employment types list

    Args:
        employment_list: List of employment dictionaries

    Returns:
        Formatted employment string
    """
    if not employment_list:
        return "Не указано"

    employment_map = {
        "full": "Полная занятость",
        "part": "Частичная занятость",
        "project": "Проектная работа",
        "volunteer": "Волонтерство",
        "probation": "Стажировка",
    }

    types = []
    for emp in employment_list:
        emp_id = emp.get("id")
        if emp_id in employment_map:
            types.append(employment_map[emp_id])

    return ", ".join(types) if types else "Не указано"


def format_schedule(schedule_list: List[Dict[str, Any]]) -> str:
    """
    Format work schedule types list

    Args:
        schedule_list: List of schedule dictionaries

    Returns:
        Formatted schedule string
    """
    if not schedule_list:
        return "Не указано"

    schedule_map = {
        "fullDay": "Полный день",
        "shift": "Сменный график",
        "flexible": "Гибкий график",
        "remote": "Удаленная работа",
        "flyInFlyOut": "Вахтовый метод",
    }

    types = []
    for sched in schedule_list:
        sched_id = sched.get("id")
        if sched_id in schedule_map:
            types.append(schedule_map[sched_id])

    return ", ".join(types) if types else "Не указано"


def parse_keywords(keywords: Union[str, List[str]]) -> List[str]:
    """
    Parse keywords from various input formats

    Args:
        keywords: Keywords as string or list

    Returns:
        List of cleaned keywords
    """
    if isinstance(keywords, str):
        # Split by comma, semicolon, or space
        return [kw.strip() for kw in re.split(r"[,;\s]+", keywords) if kw.strip()]
    elif isinstance(keywords, list):
        return [str(kw).strip() for kw in keywords if str(kw).strip()]
    else:
        return []


def is_valid_vacancy_url(url: str) -> bool:
    """
    Check if URL is a valid hh.ru vacancy URL

    Args:
        url: URL to validate

    Returns:
        True if valid hh.ru vacancy URL
    """
    pattern = r"https://hh\.ru/vacancy/\d+"
    return bool(re.match(pattern, url))


def extract_vacancy_id_from_url(url: str) -> Optional[str]:
    """
    Extract vacancy ID from hh.ru URL

    Args:
        url: hh.ru vacancy URL

    Returns:
        Vacancy ID or None if not found
    """
    pattern = r"https://hh\.ru/vacancy/(\d+)"
    match = re.search(pattern, url)
    return match.group(1) if match else None


def get_current_time() -> datetime:
    """Get current UTC time"""
    return datetime.now(timezone.utc)


def retry_async(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorator for retrying async functions

    Args:
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        backoff: Multiplier for delay on each retry
        exceptions: Exception types to catch and retry
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise last_exception

            return None

        return wrapper

    return decorator


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks

    Args:
        lst: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunked lists
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_get_nested(
    d: Optional[Dict[str, Any]], keys: List[str], default: Any = None
) -> Any:
    """
    Safely get nested dictionary values

    Args:
        d: Dictionary to search
        keys: List of keys to navigate
        default: Default value if not found

    Returns:
        Value or default
    """
    if not d or not isinstance(d, dict):
        return default

    current = d
    for key in keys:
        if key is None:
            return default
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """
    Format datetime to string

    Args:
        dt: Datetime to format
        format_str: Format string

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str) if dt else ""
