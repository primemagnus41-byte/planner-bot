import json
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models.reminder import Reminder, ReminderKind
from app.db.models.user import User
from app.db.repositories.reminder import ReminderRepository
from app.db.repositories.task import TaskRepository
from app.db.repositories.study import StudyRepository
from app.db.repositories.subscription import SubscriptionRepository
from app.utils.datetime import ensure_utc


class ReminderService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ReminderRepository(session)
        self.settings = get_settings()

    async def schedule_for_user(self, user: User) -> None:
        if not user.settings or not user.settings.reminders_enabled:
            return

        tz_str = user.settings.timezone or "Asia/Tashkent"
        try:
            user_tz = ZoneInfo(tz_str)
        except Exception:
            user_tz = ZoneInfo("Asia/Tashkent")

        now_utc = datetime.now(timezone.utc)
        user_now = now_utc.astimezone(user_tz)
        today = user_now.date()

        # Bugun va ertaga uchun vaqtlarni tekshiramiz
        for day in (today, today + timedelta(days=1)):
            date_str = day.isoformat()

            # 1. Ertalabki eslatma
            if user.settings.morning_time:
                await self._queue_fixed_time(
                    user.id,
                    ReminderKind.MORNING,
                    day,
                    user.settings.morning_time,
                    user_tz,
                    now_utc,
                    f"morning:{date_str}",
                )

            # 2. Kechki eslatma
            if user.settings.evening_time:
                await self._queue_fixed_time(
                    user.id,
                    ReminderKind.EVENING,
                    day,
                    user.settings.evening_time,
                    user_tz,
                    now_utc,
                    f"evening:{date_str}",
                )

            # 3. Kitob o'qish
            if user.settings.reading_time:
                await self._queue_fixed_time(
                    user.id,
                    ReminderKind.READING,
                    day,
                    user.settings.reading_time,
                    user_tz,
                    now_utc,
                    f"reading:{date_str}",
                )

            # 4. Spaced repetition takrorlash
            if user.settings.review_time:
                await self._queue_fixed_time(
                    user.id,
                    ReminderKind.SRS_REVIEW,
                    day,
                    user.settings.review_time,
                    user_tz,
                    now_utc,
                    f"review:{date_str}",
                )

        # 5. Obuna tugashi eslatmasi (agar 2 kundan kam qolgan bo'lsa)
        sub_repo = SubscriptionRepository(self.session)
        sub = await sub_repo.get_by_user_id(user.id)
        if sub and ensure_utc(sub.expires_at) > now_utc:
            diff = ensure_utc(sub.expires_at) - now_utc
            if diff <= timedelta(days=2):
                dedup = f"sub_exp:{ensure_utc(sub.expires_at).date().isoformat()}"
                exists = await self.repo.find_by_dedup(
                    user.id, ReminderKind.SUBSCRIPTION_EXPIRING, dedup
                )
                if not exists:
                    self.session.add(
                        Reminder(
                            user_id=user.id,
                            kind=ReminderKind.SUBSCRIPTION_EXPIRING,
                            fire_at=now_utc + timedelta(hours=1),
                            dedup_key=dedup,
                        )
                    )

    async def _queue_fixed_time(
        self,
        user_id: int,
        kind: ReminderKind,
        target_date,
        target_time: time,
        user_tz: ZoneInfo,
        now_utc: datetime,
        dedup_key: str,
    ) -> None:
        local_dt = datetime.combine(target_date, target_time, tzinfo=user_tz)
        utc_dt = local_dt.astimezone(timezone.utc)

        if utc_dt <= now_utc:
            return  # Vaqti o'tib ketgan

        exists = await self.repo.find_by_dedup(user_id, kind, dedup_key)
        if exists:
            return

        reminder = Reminder(
            user_id=user_id,
            kind=kind,
            fire_at=utc_dt,
            dedup_key=dedup_key,
        )
        self.session.add(reminder)

    async def render(self, reminder: Reminder) -> tuple[str | None, any]:
        """Eslatma matni va inline tugmalarini shakllantiradi."""
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

        user = await self.session.get(User, reminder.user_id)
        if not user:
            return None, None

        if reminder.kind == ReminderKind.MORNING:
            text = (
                "🌅 <b>Xayrli tong!</b>\n\n"
                "Bugungi kun rejalaringizni belgilab olish va samarali boshlash vaqti keldi!"
            )
            markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📋 Bugungi reja", callback_data="nav_plan")],
                    [InlineKeyboardButton(text="➕ Vazifa qo'shish", callback_data="nav_add_task")],
                ]
            )
            return text, markup

        elif reminder.kind == ReminderKind.EVENING:
            text = (
                "🌙 <b>Xayrli oqshom!</b>\n\n"
                "Bugungi vazifalaringizni sarhisob qilib, natijalarni belgilab qo'yishni unutmang."
            )
            markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Kun sarhisobi", callback_data="nav_plan")]
                ]
            )
            return text, markup

        elif reminder.kind == ReminderKind.READING:
            text = (
                "📚 <b>Mutolaa vaqti!</b>\n\n"
                "Kuniga bir necha sahifa o'qish ulkan natijalarga poydevor bo'ladi."
            )
            markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📖 Kitoblarim", callback_data="nav_books")]
                ]
            )
            return text, markup

        elif reminder.kind == ReminderKind.SRS_REVIEW:
            study_repo = StudyRepository(self.session)
            due_count = await study_repo.count_due_cards(
                reminder.user_id, datetime.now(timezone.utc)
            )
            if due_count == 0:
                return None, None  # Bugunga takrorlash yo'q, xabar yuborilmaydi
            text = (
                f"🧠 <b>Xotirani mustahkamlash vaqti!</b>\n\n"
                f"Sizda bugun takrorlanishi kerak bo'lgan <b>{due_count} ta</b> mavzu mavjud."
            )
            markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🎯 Takrorlashni boshlash", callback_data="nav_study")]
                ]
            )
            return text, markup

        elif reminder.kind == ReminderKind.SUBSCRIPTION_EXPIRING:
            admin_user = self.settings.admin_username
            text = (
                "⏳ <b>Obunangiz muddati tugamoqda!</b>\n\n"
                "Botdan uzluksiz foydalanish uchun obunangizni yangilang.\n"
                f"To'lov va ma'lumot uchun adminga murojaat qiling: @{admin_user}"
            )
            markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="💳 Obunani yangilash", callback_data="nav_sub")]
                ]
            )
            return text, markup

        return None, None
