from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.core.database import get_db_session, db_service
from src.models.database import SearchProfile, User
from src.services.hh_monitor import HHService
from src.services.job_processor import JobProcessor
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()


async def scan_jobs_for_all_profiles(bot=None):
    """
    Background task that fetches all active search profiles,
    queries HH.ru, and processes new vacancies.
    """
    logger.info("Starting background job scan for all profiles...")

    from src.core.database import get_db_service

    current_db = get_db_service()
    if not current_db:
        logger.error("Cannot run scheduled job: database service not initialized.")
        return

    # Use a new DB session for the scheduled task
    async for session in current_db.get_session():
        try:
            # 1. Fetch all active search profiles, joined with the user (to get telegram_id)
            stmt = (
                select(SearchProfile)
                .options(joinedload(SearchProfile.user))
                .where(SearchProfile.is_active == True)
            )
            result = await session.execute(stmt)
            active_profiles = result.scalars().all()

            if not active_profiles:
                logger.debug("No active search profiles found.")
                continue

            hh_client = HHService()
            processor = JobProcessor(session, bot=bot)

            total_new_jobs = 0

            # 2. Iterate and scan for each profile
            for profile in active_profiles:
                logger.info(
                    f"Scanning for profile {profile.id} (User {profile.user.telegram_id})"
                )

                # Use criteria defined in the profile JSON
                criteria = profile.search_criteria or {}

                # Always fetch the first page, sorted by publication date
                params = {
                    **criteria,
                    "order_by": "publication_time",
                    "per_page": 20,
                    "page": 0,
                }

                try:
                    results = await hh_client.fetch_vacancies(params)
                    raw_vacancies = results.get("items", [])

                    if raw_vacancies:
                        new_jobs_count = await processor.process_raw_vacancies(
                            raw_vacancies, profile
                        )
                        total_new_jobs += new_jobs_count

                except Exception as e:
                    logger.error(f"Error scanning HH.ru for profile {profile.id}: {e}")

            logger.info(
                f"Finished job scan. Found {total_new_jobs} new vacancies across all profiles."
            )

        except Exception as e:
            logger.error(f"Fatal error in job scan task: {e}")


def setup_scheduler(bot, interval_seconds: int = 300):
    """
    Configures and starts the APScheduler.

    Args:
        bot: Aiogram bot instance to pass down to the processor for sending messages.
        interval_seconds: How often to run the global scan (default 5 minutes).
    """
    global scheduler

    # Add the job scan task
    scheduler.add_job(
        scan_jobs_for_all_profiles,
        trigger=IntervalTrigger(seconds=interval_seconds),
        args=[bot],
        id="global_job_scan",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping executions if HH.ru is slow
    )

    logger.info(
        f"Configured background scheduler to run every {interval_seconds} seconds."
    )


def start_scheduler():
    """Starts the APScheduler."""
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started.")


def stop_scheduler():
    """Stops the APScheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped.")
