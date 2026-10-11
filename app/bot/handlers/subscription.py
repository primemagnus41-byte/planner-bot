from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot import texts
from app.bot.keyboards.callbacks import SubCb
from app.bot.keyboards.inline import subscription_keyboard
from app.config import get_settings
from app.db.models.user import User
from app.services.subscription import SubscriptionService

router = Router(name="subscription")
settings = get_settings()


@router.message(Command("subscribe"))
@router.message(F.text == "💎 Obuna")
async def show_subscription(message: Message, session: AsyncSession, user: User) -> None:
    sub_service = SubscriptionService(session)
    sub = await sub_service.get_or_create_subscription(user)

    status_name = {
        "trial": "Sinov muddati",
        "active": "Faol",
        "expired": "Muddati tugagan",
        "canceled": "Bekor qilingan",
    }.get(sub.status.value, sub.status.value)

    plan_name = {
        "trial": "Sinov",
        "monthly": "1 oylik",
        "quarterly": "3 oylik",
        "annual": "1 yillik",
    }.get(sub.plan.value, sub.plan.value)

    info_text = texts.SUBSCRIPTION_INFO.format(
        status=status_name,
        plan=plan_name,
        expires_at=sub.expires_at.strftime("%d.%m.%Y %H:%M"),
        admin_username=settings.admin_username,
    )

    await message.answer(
        info_text,
        reply_markup=subscription_keyboard(settings.admin_username),
    )


@router.callback_query(SubCb.filter(F.action == "plans"))
async def show_plans_callback(call: CallbackQuery) -> None:
    plans_text = texts.PLANS_TEXT.format(admin_username=settings.admin_username)
    await call.message.edit_text(
        plans_text,
        reply_markup=subscription_keyboard(settings.admin_username),
    )
    await call.answer()
