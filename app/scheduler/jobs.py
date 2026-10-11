import logging
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from sqlalchemy import select

from app.db.base import async_session_maker
from app.db.models.reminder import Reminder
from app.db.models.user import User, UserStatus
from app.services.reminder import ReminderService

log = logging.getLogger(__name__)


async def plan_daily_reminders() -> None:
    """Keyingi 36 soat uchun eslatmalarni bazaga yozadi."""
    async with async_session_maker() as session:
        users = await session.scalars(
            select(User).where(User.status.in_([UserStatus.APPROVED, UserStatus.PENDING]))
        )
        service = ReminderService(session)
        for user in users:
            if not user.settings or not user.settings.reminders_enabled:
                continue
            await service.schedule_for_user(user)
        await session.commit()


async def dispatch_due_reminders(bot: Bot) -> None:
    now = datetime.now(timezone.utc)
    async with async_session_maker() as session:
        service = ReminderService(session)
        rows = await service.repo.list_due(now=now, limit=100)

        for rem in rows:
            text, markup = await service.render(rem)
            if text is None:  # Masalan bugun takrorlash yo'q
                rem.sent_at = now
                continue
            try:
                await bot.send_message(rem.user_id, text, reply_markup=markup)
                rem.sent_at = datetime.now(timezone.utc)
            except TelegramRetryAfter as e:
                rem.fire_at = now + timedelta(seconds=e.retry_after + 1)
                rem.attempts += 1
                break
            except TelegramForbiddenError:
                user = await session.get(User, rem.user_id)
                if user:
                    user.status = UserStatus.BLOCKED_BOT
                rem.sent_at = now
                rem.last_error = "user blocked bot"
            except Exception as e:
                rem.attempts += 1
                rem.last_error = str(e)[:500]
                log.exception("Reminder send failed id=%s", rem.id)

        await session.commit()


async def nightly_backup(bot: Bot, admin_id: int, db_path: str) -> None:
    """SQLite faylini adminga yuboradi — ma'lumotlarni yo'qolishdan asraydi."""
    import os
    from aiogram.types import FSInputFile

    if not os.path.exists(db_path):
        return

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    try:
        await bot.send_document(
            admin_id,
            FSInputFile(db_path, filename=f"planner-{stamp}.db"),
            caption="🗄 <b>Kunlik ma'lumotlar bazasi nusxasi (Backup)</b>",
        )
    except Exception as e:
        log.exception("Backup send failed: %s", e)
