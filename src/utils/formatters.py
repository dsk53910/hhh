from typing import Dict, Any
from src.utils.helpers import (
    format_salary,
    format_experience,
    format_schedule,
    format_employment,
)


def format_vacancy_message(vacancy: Dict[str, Any]) -> str:
    """
    Formats a raw HH.ru vacancy dictionary into a Telegram-friendly HTML string.

    Args:
        vacancy: Dictionary containing vacancy data from HH.ru API

    Returns:
        Formatted HTML string ready to be sent via Telegram
    """
    title = vacancy.get("name", "Без названия")

    # Handle nested employer data
    employer_data = vacancy.get("employer")
    employer = (
        employer_data.get("name", "Неизвестная компания")
        if employer_data
        else "Неизвестная компания"
    )

    url = vacancy.get("alternate_url", "")

    # Format salary and meta info
    salary = format_salary(vacancy.get("salary"))

    # Experience, Schedule, Employment come as dicts with 'id' and 'name'
    exp_dict = vacancy.get("experience")
    exp = format_experience(exp_dict.get("id") if exp_dict else None)

    sched_dict = vacancy.get("schedule")
    schedule = format_schedule([sched_dict] if sched_dict else [])

    emp_dict = vacancy.get("employment")
    employment = format_employment([emp_dict] if emp_dict else [])

    # Process snippet (short description) and handle HH.ru highlight tags
    snippet = vacancy.get("snippet") or {}
    req = snippet.get("requirement", "") or ""
    res = snippet.get("responsibility", "") or ""

    # Clean up HH highlights to Telegram bold tags
    combined_snippet = f"{req} {res}".replace("<highlighttext>", "<b>").replace(
        "</highlighttext>", "</b>"
    )

    # Build message
    message = f"🔥 <b>{title}</b>\n"
    message += f"🏢 <b>{employer}</b>\n"
    message += f"💰 {salary}\n"
    message += f"📊 {exp} | 🕒 {schedule} | 💼 {employment}\n\n"

    if combined_snippet.strip():
        # Truncate if too long, keeping HTML tags safe-ish (ideally use a proper HTML truncator)
        clean_snippet = (
            combined_snippet[:300] + "..."
            if len(combined_snippet) > 300
            else combined_snippet
        )
        message += f"📝 <i>{clean_snippet}</i>\n"

    return message
