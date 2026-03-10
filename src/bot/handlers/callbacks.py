from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from datetime import datetime

from src.core.database import with_db_session
from src.models.database import JobApplication, ApplicationStatus, Vacancy, User
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = Router(name="callbacks_router")


@router.callback_query(F.data.startswith("apply_"))
@with_db_session
async def process_apply(session, callback: CallbackQuery):
    """
    Handle the 'Apply' button click on a vacancy message.
    """
    await callback.answer()  # Acknowledge the callback immediately

    if not callback.message or not callback.data:
        return

    # data format: apply_12345678 (where 12345678 is the HH.ru vacancy ID)
    hh_vacancy_id = callback.data.split("_")[1]
    telegram_id = callback.from_user.id
    msg = callback.message

    try:
        # 1. Get our internal User ID
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            if hasattr(msg, "reply"):
                await msg.reply("Пользователь не найден в базе данных.")
            return

        # 2. Get the internal Vacancy ID
        stmt = select(Vacancy).where(Vacancy.vacancy_id == hh_vacancy_id)
        result = await session.execute(stmt)
        vacancy = result.scalar_one_or_none()

        if not vacancy:
            if hasattr(msg, "reply"):
                await msg.reply("Ошибка: Вакансия не найдена в базе данных.")
            return

        # 3. Check if already applied
        stmt = select(JobApplication).where(
            JobApplication.user_id == user.id, JobApplication.vacancy_id == vacancy.id
        )
        result = await session.execute(stmt)
        existing_app = result.scalar_one_or_none()

        if existing_app:
            if hasattr(msg, "edit_reply_markup"):
                await msg.edit_reply_markup(reply_markup=None)
            if hasattr(msg, "reply"):
                await msg.reply(
                    f"Вы уже откликались на вакансию <b>{vacancy.title}</b>.",
                    parse_mode="HTML",
                )
            return

        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        # 4. Attempt real application via HH.ru API
        from src.services.hh_monitor import HHService

        hh_client = HHService()

        # Check if user has configured their HH tokens
        if not hh_client.settings.hh.api_key or not hh_client.settings.hh.resume_id:
            if hasattr(msg, "reply"):
                await msg.reply(
                    "❌ <b>Ошибка:</b> Не настроен токен HH.ru или ID резюме.\n\n"
                    "Добавьте `HH_API_KEY` и `HH_RESUME_ID` в ваш файл `.env`.",
                    parse_mode="HTML",
                )
            return

        if hasattr(msg, "edit_reply_markup"):
            await msg.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="⏳ Отправка отклика...",
                                callback_data="processing",
                            )
                        ]
                    ]
                )
            )

        # We can pass an empty message, or a standard cover letter here
        success = await hh_client.apply_to_vacancy(
            vacancy_id=hh_vacancy_id,
            resume_id=hh_client.settings.hh.resume_id,
            message="Здравствуйте! Меня очень заинтересовала ваша вакансия. Буду рад обсудить детали на интервью.",
        )

        if success:
            # 5. Create JobApplication record (Save to Database)
            application = JobApplication(
                user_id=user.id,
                vacancy_id=vacancy.id,
                status=ApplicationStatus.SENT,
                applied_at=datetime.utcnow(),
            )
            session.add(application)
            await session.commit()

            logger.info(
                f"User {telegram_id} successfully applied to vacancy {hh_vacancy_id}"
            )

            # 6. Update UI to success
            new_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Успешно откликнулись!",
                            callback_data="already_applied",
                        )
                    ],
                    [InlineKeyboardButton(text="🔗 Открыть на HH.ru", url=vacancy.url)],
                ]
            )
            if hasattr(msg, "edit_reply_markup"):
                await msg.edit_reply_markup(reply_markup=new_keyboard)

        else:
            # Revert UI on failure
            from src.bot.keyboards.inline import get_vacancy_keyboard

            if hasattr(msg, "edit_reply_markup"):
                await msg.edit_reply_markup(
                    reply_markup=get_vacancy_keyboard(hh_vacancy_id, vacancy.url)
                )
            if hasattr(msg, "reply"):
                await msg.reply(
                    "❌ Не удалось отправить отклик через HH.ru.\n"
                    "Возможно, вы уже откликались на эту вакансию, резюме не подходит по требованиям, либо токен устарел."
                )

    except Exception as e:
        logger.error(
            f"Error processing apply callback for {hh_vacancy_id}: {e}", exc_info=True
        )
        await session.rollback()
        if hasattr(msg, "reply"):
            await msg.reply("Произошла ошибка при сохранении отклика.")


@router.callback_query(F.data == "already_applied")
async def process_already_applied(callback: CallbackQuery):
    await callback.answer("Вы уже откликнулись на эту вакансию!", show_alert=True)
