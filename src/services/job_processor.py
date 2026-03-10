import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import Vacancy, MonitoredJob, SearchProfile, JobSource
from src.utils.logger import get_logger
from src.utils.helpers import safe_get_nested
from src.services.hh_monitor import HHService
from src.utils.formatters import format_vacancy_message

logger = get_logger(__name__)


class JobProcessor:
    """
    Central logic for matching, saving, and broadcasting job updates.
    """

    def __init__(self, db_session: AsyncSession, bot=None):
        self.db = db_session
        self.bot = bot  # aiogram Bot instance, optional for testing
        self.hh_client = HHService()

    async def process_raw_vacancies(
        self, raw_vacancies: List[Dict[str, Any]], profile: SearchProfile
    ) -> int:
        """
        Process raw vacancies fetched from HH.ru.
        - Check if they exist in the DB.
        - Create Vacancy if new.
        - Create MonitoredJob link to the user's profile.
        - Send Telegram notification if the link is new.

        Returns:
            Number of newly found and notified jobs.
        """
        new_jobs_count = 0

        for raw in raw_vacancies:
            hh_id = str(raw.get("id"))
            if not hh_id:
                continue

            # 1. Check if Vacancy exists globally in our DB
            stmt = select(Vacancy).where(Vacancy.vacancy_id == hh_id)
            result = await self.db.execute(stmt)
            vacancy = result.scalar_one_or_none()

            if not vacancy:
                # 2. Create New Vacancy
                vacancy = self._create_vacancy_from_raw(raw)
                self.db.add(vacancy)
                await self.db.flush()  # Flush to get the ID
                logger.debug(f"Created new Vacancy ID: {vacancy.id} (HH: {hh_id})")

            # 3. Check if MonitoredJob link exists for this specific profile
            link_stmt = select(MonitoredJob).where(
                MonitoredJob.search_profile_id == profile.id,
                MonitoredJob.vacancy_id == vacancy.id,
            )
            link_result = await self.db.execute(link_stmt)
            monitored_job = link_result.scalar_one_or_none()

            if not monitored_job:
                # 4. Create link and Notify User
                monitored_job = MonitoredJob(
                    search_profile_id=profile.id,
                    vacancy_id=vacancy.id,
                    is_matched=True,
                    is_notified=False,
                )
                self.db.add(monitored_job)

                # Format and send message
                await self._notify_user(profile.user_id, raw, monitored_job)
                new_jobs_count += 1

        # Commit all DB transactions (Vacancies + MonitoredJobs) at the end of the batch
        await self.db.commit()
        return new_jobs_count

    def _create_vacancy_from_raw(self, raw: Dict[str, Any]) -> Vacancy:
        """Map raw HH JSON to SQLAlchemy Vacancy model."""

        # Parse publication date (e.g., "2023-10-24T12:30:00+0300")
        published_at = None
        pub_str = raw.get("published_at")
        if pub_str:
            try:
                # Strip timezone info or handle it
                clean_pub = pub_str.split("+")[0]
                published_at = datetime.fromisoformat(clean_pub)
            except ValueError:
                pass

        return Vacancy(
            vacancy_id=str(raw.get("id")),
            source=JobSource.HH_RU,
            url=raw.get("alternate_url", ""),
            title=raw.get("name", "Без названия"),
            company_name=safe_get_nested(raw, ["employer", "name"]),
            company_url=safe_get_nested(raw, ["employer", "alternate_url"]),
            # Salary
            salary_from=safe_get_nested(raw, ["salary", "from"]),
            salary_to=safe_get_nested(raw, ["salary", "to"]),
            salary_currency=safe_get_nested(raw, ["salary", "currency"]),
            salary_gross=safe_get_nested(raw, ["salary", "gross"]),
            # Meta
            experience=safe_get_nested(raw, ["experience", "id"]),
            employment_type=safe_get_nested(raw, ["employment", "id"]),
            schedule=safe_get_nested(raw, ["schedule", "id"]),
            # Location
            area=safe_get_nested(raw, ["area", "name"]),
            address=safe_get_nested(raw, ["address", "raw"]),
            published_at=published_at,
            raw_data=raw,
        )

    async def _notify_user(
        self, telegram_id: int, raw_vacancy: Dict[str, Any], monitored_job: MonitoredJob
    ):
        """Send formatted message via Telegram Bot."""
        if not self.bot:
            logger.debug(
                f"Skipping notification (No bot configured) for user {telegram_id}"
            )
            return

        try:
            msg_html = format_vacancy_message(raw_vacancy)
            from src.bot.keyboards.inline import get_vacancy_keyboard

            keyboard = get_vacancy_keyboard(
                hh_vacancy_id=raw_vacancy.get("id"),
                url=raw_vacancy.get("alternate_url", ""),
            )

            # In aiogram 3.x, bot.send_message is asynchronous
            # Note: We must use the user's actual telegram_id, NOT the database user_id!
            # The function parameter here is actually user_id (the foreign key to User table), we need telegram_id.

            # 1. Fetch the user to get their real telegram_id
            from sqlalchemy import select
            from src.models.database import User

            stmt = select(User).where(User.id == telegram_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user or not user.telegram_id:
                logger.error(
                    f"Cannot notify user {telegram_id}: No telegram_id found in DB."
                )
                return

            real_telegram_id = user.telegram_id

            await self.bot.send_message(
                chat_id=real_telegram_id,
                text=msg_html,
                parse_mode="HTML",
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
            monitored_job.is_notified = True
            monitored_job.notified_at = datetime.utcnow()
            logger.info(
                f"Notified telegram_id {real_telegram_id} about vacancy {raw_vacancy.get('id')}"
            )
        except Exception as e:
            logger.error(
                f"Failed to notify telegram_id {real_telegram_id if 'real_telegram_id' in locals() else telegram_id}: {e}"
            )
