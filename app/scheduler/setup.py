import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.config import get_settings
from app.scheduler import jobs

settings = get_settings()


def create_scheduler(bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(
        timezone="UTC",
        job_defaults={"coalesce": True, "max_instances": 1, "misfire_grace_time": 300},
    )

    scheduler.add_job(
        jobs.plan_daily_reminders,
        CronTrigger(hour=0, minute=5),
        id="plan_daily",
        replace_existing=True,
    )

    scheduler.add_job(
        jobs.dispatch_due_reminders,
        IntervalTrigger(minutes=1),
        args=[bot],
        id="dispatch",
        replace_existing=True,
    )

    db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
    scheduler.add_job(
        jobs.nightly_backup,
        CronTrigger(hour=20, minute=0),
        args=[bot, settings.admin_id, db_path],
        id="backup",
        replace_existing=True,
    )

    return scheduler
