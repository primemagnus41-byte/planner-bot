from aiogram import Router

from app.bot.handlers.common import router as common_router
from app.bot.handlers.subscription import router as subscription_router
from app.bot.handlers.admin import router as admin_router
from app.bot.handlers.tasks import router as tasks_router
from app.bot.handlers.reading import router as reading_router
from app.bot.handlers.study import router as study_router
from app.bot.handlers.ideas import router as ideas_router
from app.bot.handlers.settings import router as settings_router
from app.bot.handlers.stats import router as stats_router


def get_main_router() -> Router:
    main_router = Router(name="main_router")
    main_router.include_router(common_router)
    main_router.include_router(subscription_router)
    main_router.include_router(admin_router)
    main_router.include_router(tasks_router)
    main_router.include_router(reading_router)
    main_router.include_router(study_router)
    main_router.include_router(ideas_router)
    main_router.include_router(settings_router)
    main_router.include_router(stats_router)
    return main_router
