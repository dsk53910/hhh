from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router
from sqlalchemy import select

from src.bot.handlers.callbacks import router as callbacks_router
from src.bot.handlers.commands import router as commands_router
from src.core.database import with_db_session
from src.models.database import User
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = Router(name="core_router")


@router.message(CommandStart())
@with_db_session
async def cmd_start(session, message: Message):
    """
    Handle the /start command.
    Checks if the user exists in the database, creates them if not.
    """
    telegram_id = message.from_user.id

    # 1. Check if user already exists
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        # 2. Create new user
        user = User(
            telegram_id=telegram_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            is_active=True,
            is_admin=False,  # Default to false, can be overridden by config later
        )
        session.add(user)
        await session.commit()
        logger.info(
            f"New user registered: {telegram_id} ({message.from_user.first_name})"
        )

        welcome_text = (
            f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
            f"Я — бот для автоматического мониторинга свежих вакансий на HH.ru.\n\n"
            f"Вам больше не нужно постоянно обновлять сайт. Просто настройте фильтры, "
            f"и я буду присылать подходящие варианты сразу, как они появятся.\n\n"
            f"<i>Нажмите /search, чтобы создать свой первый поисковый профиль.</i>"
        )
    else:
        # User already exists
        logger.debug(f"Returning user: {telegram_id}")
        welcome_text = (
            f"👋 С возвращением, {message.from_user.first_name}!\n\n"
            f"Ваш мониторинг активен. Используйте меню для управления вашими поисками.\n\n"
            f"<i>(Меню настройки критериев в разработке...)</i>"
        )

    await message.answer(welcome_text)


def setup_handlers(dp: Dispatcher):
    """Registers all routers into the main Dispatcher."""
    dp.include_router(router)
    dp.include_router(callbacks_router)
    dp.include_router(commands_router)
