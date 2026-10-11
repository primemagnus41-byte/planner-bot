from typing import Any
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot import texts
from app.bot.keyboards.inline import subscription_keyboard
from app.config import get_settings
from app.db.models.user import UserStatus
from app.services.subscription import SubscriptionService
from app.services.user import UserService

settings = get_settings()


class AccessMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict[str, Any]) -> Any:
        tg_user = data.get("event_from_user")
        if tg_user is None:
            return await handler(event, data)

        session: AsyncSession = data["session"]
        user_service = UserService(session)
        sub_service = SubscriptionService(session)

        user, created = await user_service.get_or_create(
            tg_id=tg_user.id,
            full_name=tg_user.full_name,
            username=tg_user.username,
        )
        data["user"] = user
        data["is_admin"] = tg_user.id == settings.admin_id

        if data["is_admin"]:
            if user.status != UserStatus.APPROVED:
                await user_service.set_status(user, UserStatus.APPROVED)
            return await handler(event, data)

        if user.status == UserStatus.BANNED:
            return await _reply(event, texts.ACCESS_BANNED)

        # Obunani tekshiramiz
        has_access, reason, sub = await sub_service.check_access(user, is_admin=False)
        data["subscription"] = sub

        # Yangi foydalanuvchi sinov muddati olgan bo'lsa
        if created and reason == "trial":
            await session.commit()

        if has_access:
            return await handler(event, data)

        # Agar obunasi tugagan bo'lsa, start yoki obuna tugmalariga ruxsat beramiz
        if isinstance(event, Message):
            if event.text and (event.text.startswith("/start") or event.text in ["💎 Obuna", "/help"]):
                return await handler(event, data)
        elif isinstance(event, CallbackQuery):
            if event.data and (event.data.startswith("sub:") or event.data == "nav_sub"):
                return await handler(event, data)

        expired_text = texts.ACCESS_EXPIRED.format(admin_username=settings.admin_username)
        markup = subscription_keyboard(settings.admin_username)
        return await _reply(event, expired_text, markup=markup)


async def _reply(event: TelegramObject, text: str, markup=None) -> None:
    if isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    elif isinstance(event, CallbackQuery):
        await event.answer(show_alert=False)
        if event.message:
            await event.message.answer(text, reply_markup=markup)
