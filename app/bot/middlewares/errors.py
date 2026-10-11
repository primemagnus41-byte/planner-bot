import logging
from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.bot import texts

log = logging.getLogger(__name__)


class ErrorMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data):
        try:
            return await handler(event, data)
        except TelegramRetryAfter:
            raise
        except TelegramForbiddenError:
            log.warning("User blocked the bot")
        except Exception:
            log.exception("Unhandled error in handler")
            if isinstance(event, Message):
                await event.answer(texts.GENERIC_ERROR)
            elif isinstance(event, CallbackQuery):
                await event.answer(texts.GENERIC_ERROR, show_alert=True)
