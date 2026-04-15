from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select
from datetime import datetime

from src.core.database import with_db_session
from src.models.database import User, SearchProfile
from src.services.hh_monitor import HHService
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = Router(name="commands_router")


# Define the states for our dialog
class CreateProfileStates(StatesGroup):
    waiting_for_keywords = State()
    waiting_for_city = (
        State()
    )  # We'll hardcode Moscow (Area 1) for now, but keep state for future


@router.message(Command("search"))
@with_db_session
async def cmd_search_start(session, message: Message, state: FSMContext):
    """Starts the profile creation dialog."""

    # First, verify user exists
    if not message.from_user:
        return

    stmt = select(User).where(User.telegram_id == message.from_user.id)
    user = (await session.execute(stmt)).scalar_one_or_none()

    if not user:
        await message.answer("Сначала нажмите /start для регистрации в системе.")
        return

    await state.set_state(CreateProfileStates.waiting_for_keywords)
    await message.answer(
        "🔍 <b>Создание нового поиска</b>\n\n"
        "Введите начало должности (например: <i>Разработчик</i>, <i>Аналитик</i>) и я предложу варианты:",
        parse_mode="HTML",
    )


@router.message(CreateProfileStates.waiting_for_keywords)
async def process_keywords_suggest(message: Message, state: FSMContext):
    """Takes input and fetches suggestions from HH.ru."""
    if not message.text:
        return
    keywords = message.text.strip()

    if len(keywords) < 2:
        await message.answer("Слишком короткий запрос. Пожалуйста, напишите подробнее:")
        return

    # Fetch suggestions from HH.ru
    hh_client = HHService()
    suggestions = await hh_client.get_keyword_suggestions(keywords)

    if not suggestions:
        # If no suggestions, use raw input directly and move to city selection
        await state.update_data(search_type="keyword", value=keywords)
        await state.set_state(CreateProfileStates.waiting_for_city)
        await message.answer(
            f"✅ Сохранено: <b>{keywords}</b>\n\n"
            f"Теперь введите город или страну для поиска (например: <i>Москва</i>, <i>Казахстан</i>):",
            parse_mode="HTML",
        )
        return

    # Build inline keyboard with suggestions
    # We only take top 5 to not overflow Telegram's inline keyboard limits
    buttons = []
    for sug in suggestions[:5]:
        buttons.append(
            [InlineKeyboardButton(text=sug, callback_data=f"prof_{sug[:40]}")]
        )

    # Add an option to use exactly what the user typed
    buttons.append(
        [
            InlineKeyboardButton(
                text=f"✅ Искать точно: {keywords[:30]}",
                callback_data=f"prof_{keywords[:40]}",
            )
        ]
    )

    # Add IT Category option
    buttons.append(
        [
            InlineKeyboardButton(
                text="💻 Искать ВСЕ в сфере IT (Информационные технологии)",
                callback_data="cat_11",  # 11 is the ID for IT category in HH.ru
            )
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(
        "Я нашел несколько вариантов на HH.ru. Выберите подходящий:",
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("prof_"))
@with_db_session
async def process_profile_selection(
    session, callback: CallbackQuery, state: FSMContext
):
    """Handles the selection of a profession from the suggestion list."""
    await callback.answer()

    if not callback.data:
        return

    # Extract the chosen keyword
    chosen_keyword = callback.data.split("prof_")[1]

    # Remove the keyboard from the previous message
    if callback.message:
        try:
            msg = callback.message
            if hasattr(msg, "edit_reply_markup") and callable(
                getattr(msg, "edit_reply_markup", None)
            ):
                # Ignore type checking here since aiogram Message definitely has it,
                # but InaccessibleMessage doesn't, causing pyright to complain
                await msg.edit_reply_markup(reply_markup=None)  # type: ignore
        except Exception:
            pass

    await state.update_data(search_type="keyword", value=chosen_keyword)
    await state.set_state(CreateProfileStates.waiting_for_city)

    if callback.message:
        await callback.message.answer(
            f"✅ Выбрано: <b>{chosen_keyword}</b>\n\n"
            f"Теперь введите город или страну для поиска (например: <i>Москва</i>, <i>Минск</i>, <i>Казахстан</i>):",
            parse_mode="HTML",
        )


@router.callback_query(F.data.startswith("cat_"))
@with_db_session
async def process_category_selection(
    session, callback: CallbackQuery, state: FSMContext
):
    """Handles the selection of an entire professional category (like IT)."""
    await callback.answer()

    if not callback.data:
        return

    # Extract the chosen category ID
    category_id = callback.data.split("cat_")[1]

    if callback.message:
        try:
            msg = callback.message
            if hasattr(msg, "edit_reply_markup") and callable(
                getattr(msg, "edit_reply_markup", None)
            ):
                await msg.edit_reply_markup(reply_markup=None)  # type: ignore
        except Exception:
            pass

    await state.update_data(search_type="category", value=category_id)
    await state.set_state(CreateProfileStates.waiting_for_city)

    if callback.message:
        await callback.message.answer(
            f"✅ Выбрана вся сфера IT\n\n"
            f"Теперь введите город или страну для поиска (например: <i>Москва</i>, <i>Минск</i>, <i>Тбилиси</i>):",
            parse_mode="HTML",
        )


@router.message(CreateProfileStates.waiting_for_city)
async def process_city_suggest(message: Message, state: FSMContext):
    """Takes input and fetches suggestions for areas (cities/countries) from HH.ru."""
    if not message.text:
        return
    city_name = message.text.strip()

    if len(city_name) < 2:
        await message.answer(
            "Слишком короткое название. Пожалуйста, напишите подробнее:"
        )
        return

    hh_client = HHService()
    suggestions = await hh_client.get_area_suggestions(city_name)

    if not suggestions:
        await message.answer(
            "Я не смог найти такой регион на HH.ru. Попробуйте написать по-другому (например: Россия, Москва, Тбилиси):"
        )
        return

    buttons = []
    for sug in suggestions[:6]:
        # Callback data length limit in Telegram is 64 bytes.
        # "area_12345" is safe. We will save the text in FSM if needed, or just look it up later.
        buttons.append(
            [InlineKeyboardButton(text=sug["text"], callback_data=f"area_{sug['id']}")]
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(
        "Выберите точный регион или город из списка:",
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("area_"))
@with_db_session
async def process_area_selection(session, callback: CallbackQuery, state: FSMContext):
    """Finalizes the profile creation after an area is selected."""
    await callback.answer()

    if not callback.data:
        return

    area_id = callback.data.split("area_")[1]

    if callback.message:
        try:
            msg = callback.message
            if hasattr(msg, "edit_reply_markup") and callable(
                getattr(msg, "edit_reply_markup", None)
            ):
                await msg.edit_reply_markup(reply_markup=None)  # type: ignore
        except Exception:
            pass

    # Retrieve saved search type and value
    data = await state.get_data()
    search_type = data.get("search_type")
    search_value = data.get("value")

    if not search_type or not search_value:
        if callback.message:
            await callback.message.answer(
                "Ой, что-то пошло не так. Давайте начнем заново: /search"
            )
        await state.clear()
        return

    # Build criteria
    criteria = {"area": area_id}
    profile_name = "Новый поиск"

    if search_type == "keyword":
        criteria["text"] = search_value
        profile_name = search_value[:50]
    elif search_type == "category":
        criteria["professional_role"] = search_value
        profile_name = "IT Сфера"

    # Save to database
    stmt = select(User).where(User.telegram_id == callback.from_user.id)
    user = (await session.execute(stmt)).scalar_one_or_none()

    if user:
        profile = SearchProfile(
            user_id=user.id,
            name=profile_name,
            search_criteria=criteria,
            is_active=True,
        )
        session.add(profile)
        await session.commit()
        logger.info(
            f"User {user.telegram_id} created profile: {profile_name} in area {area_id}"
        )

    await state.clear()

    if callback.message:
        await callback.message.answer(
            f"✅ <b>Поиск успешно создан и запущен!</b>\n\n"
            f"Теперь я каждые 5 минут буду проверять этот фильтр на HH.ru и присылать вам новые вакансии.",
            parse_mode="HTML",
        )


# Remove the old unused helper functions
async def finalize_profile_creation(message: Message, state: FSMContext, keywords: str):
    pass


async def finalize_profile_creation_from_callback(
    session, callback: CallbackQuery, state: FSMContext, keywords: str
):
    pass


async def _save_profile_to_db(session, user, keywords: str):
    pass
