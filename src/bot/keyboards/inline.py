from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_vacancy_keyboard(hh_vacancy_id: str, url: str) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard for a new vacancy message.

    Args:
        hh_vacancy_id: The external ID from HH.ru
        url: The direct link to the vacancy

    Returns:
        InlineKeyboardMarkup object with 'Apply' and 'View' buttons
    """
    buttons = [
        [
            InlineKeyboardButton(
                text="🚀 Откликнуться (через бота)",
                callback_data=f"apply_{hh_vacancy_id}",
            )
        ],
        [InlineKeyboardButton(text="🔗 Открыть на HH.ru", url=url)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
