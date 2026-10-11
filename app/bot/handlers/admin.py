from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.subscription import SubscriptionPlan
from app.db.models.user import User
from app.services.stats import StatsService
from app.services.subscription import SubscriptionService

router = Router(name="admin")


@router.message(Command("admin"))
@router.message(F.text == "👑 Admin panel")
async def admin_panel(message: Message, session: AsyncSession, is_admin: bool) -> None:
    if not is_admin:
        return

    stats_service = StatsService(session)
    overview = await stats_service.admin_overview()

    users_text = "\n".join([f"• {k}: {v} ta" for k, v in overview["users"].items()]) or "Hozircha yo'q"
    subs_text = "\n".join([f"• {k}: {v} ta" for k, v in overview["subscriptions"].items()]) or "Hozircha yo'q"

    text = (
        "👑 <b>Admin Boshqaruv Paneli</b>\n\n"
        f"👥 <b>Foydalanuvchilar:</b>\n{users_text}\n\n"
        f"💎 <b>Obunalar:</b>\n{subs_text}\n\n"
        "<b>Buyruqlar:</b>\n"
        "• <code>/grant &lt;user_id&gt; &lt;kun&gt;</code> — Foydalanuvchiga obuna berish\n"
        "<i>Masalan: <code>/grant 123456789 30</code></i>"
    )
    await message.answer(text)


@router.message(Command("grant"))
async def admin_grant_subscription(
    message: Message, session: AsyncSession, is_admin: bool
) -> None:
    if not is_admin:
        return

    parts = message.text.split()
    if len(parts) < 3:
        await message.answer(
            "⚠️ Noto'g'ri format!\n"
            "To'g'ri shakl: <code>/grant &lt;user_id&gt; &lt;kun&gt;</code>\n"
            "Masalan: <code>/grant 123456789 30</code>"
        )
        return

    try:
        target_user_id = int(parts[1])
        days = int(parts[2])
    except ValueError:
        await message.answer("⚠️ user_id va kun son bo'lishi kerak.")
        return

    sub_service = SubscriptionService(session)
    sub = await sub_service.grant_subscription(
        user_id=target_user_id,
        plan=SubscriptionPlan.MONTHLY if days <= 31 else SubscriptionPlan.QUARTERLY,
        days=days,
        notes="Admin tomonidan qo'lda berildi",
    )

    exp_str = sub.expires_at.strftime("%d.%m.%Y %H:%M")
    await message.answer(
        f"✅ <b>Foydalanuvchi {target_user_id} ga {days} kunlik obuna berildi!</b>\n"
        f"Amal qilish muddati: <b>{exp_str}</b> gacha."
    )

    # Foydalanuvchini ogohlantirish
    try:
        await message.bot.send_message(
            target_user_id,
            f"🎉 <b>Tabriklaymiz!</b>\n\n"
            f"Sizga <b>{days} kunlik</b> obuna berildi!\n"
            f"Yangi amal qilish muddati: <b>{exp_str}</b> gacha.\n"
            "Botdan bemalol to'liq foydalanishingiz mumkin."
        )
    except Exception:
        pass
