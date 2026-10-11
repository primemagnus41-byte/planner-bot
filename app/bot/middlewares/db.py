from typing import Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.db.base import async_session_maker


class DbSessionMiddleware(BaseMiddleware):
    """Har update uchun bitta session + bitta tranzaksiya."""

    async def __call__(self, handler, event: TelegramObject, data: dict[str, Any]) -> Any:
        async with async_session_maker() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
