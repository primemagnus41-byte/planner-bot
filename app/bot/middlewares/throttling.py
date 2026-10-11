import time
from collections import defaultdict
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate: float = 0.5) -> None:
        self.rate = rate
        self._last: dict[int, float] = defaultdict(float)

    async def __call__(self, handler, event: TelegramObject, data):
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)
        now = time.monotonic()
        if now - self._last[user.id] < self.rate:
            if isinstance(event, CallbackQuery):
                await event.answer()
            return
        self._last[user.id] = now
        return await handler(event, data)
