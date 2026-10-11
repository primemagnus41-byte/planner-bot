import asyncio
import logging
import logging.handlers
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.handlers import get_main_router
from app.bot.middlewares.access import AccessMiddleware
from app.bot.middlewares.db import DbSessionMiddleware
from app.bot.middlewares.errors import ErrorMiddleware
from app.bot.middlewares.throttling import ThrottlingMiddleware
from app.config import get_settings
from app.scheduler.setup import create_scheduler


def build_storage(settings):
    if settings.redis_url:
        from aiogram.fsm.storage.redis import RedisStorage
        return RedisStorage.from_url(settings.redis_url)
    return MemoryStorage()


async def main() -> None:
    settings = get_settings()

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    handlers: list[logging.Handler] = [
        logging.handlers.RotatingFileHandler(
            "data/app.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
    ]
    if sys.stdout is not None:
        handlers.append(logging.StreamHandler(sys.stdout))

    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
    )

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=build_storage(settings))

    # Middleware tartibi: Xato -> DB sessiya -> Kirish & Obuna -> Throttle
    for observer in (dp.message, dp.callback_query):
        observer.middleware(ErrorMiddleware())
        observer.middleware(DbSessionMiddleware())
        observer.middleware(AccessMiddleware())
        observer.middleware(ThrottlingMiddleware())

    dp.include_router(get_main_router())

    scheduler = create_scheduler(bot)
    scheduler.start()

    logging.info("Bot ishga tushmoqda...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
