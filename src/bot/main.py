import asyncio
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from src.core.config import get_settings
from src.core.database import init_database
from src.core.scheduler import setup_scheduler, start_scheduler, stop_scheduler
from src.utils.logger import setup_logging, get_logger
from src.bot.handlers import setup_handlers

logger = get_logger(__name__)


async def main():
    # Load configuration
    settings = get_settings()

    # Configure logging
    setup_logging(
        log_level=settings.logging.level,
        log_file=settings.logging.file,
        json_format=settings.logging.json_format,
    )

    logger.info("Starting HHH Bot application...")

    # Initialize Database
    try:
        db_service = await init_database(
            database_url=settings.get_database_url(),
            echo=settings.database.echo,
            pool_size=settings.database.pool_size,
        )
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)

    # Initialize Bot & Dispatcher
    bot_token = settings.bot.token
    if not bot_token or bot_token.startswith("${"):
        logger.error("BOT_TOKEN is missing or not substituted in configuration.")
        sys.exit(1)

    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())

    # Include handler routers
    setup_handlers(dp)

    # Setup Background Task Scheduler for HH.ru polling
    # Uses the search_interval from config (default 5 mins)
    setup_scheduler(bot=bot, interval_seconds=settings.hh.search_interval)
    start_scheduler()

    logger.info("Bot and Scheduler initialized successfully. Starting polling...")

    try:
        if settings.bot.drop_pending_updates:
            await bot.delete_webhook(drop_pending_updates=True)

        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error during bot polling: {e}")
    finally:
        logger.info("Shutting down...")
        stop_scheduler()
        await bot.session.close()
        await db_service.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped cleanly.")
