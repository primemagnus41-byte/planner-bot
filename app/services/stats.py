from datetime import date, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.task import TaskStatus
from app.db.repositories.task import TaskRepository
from app.db.repositories.reading import ReadingRepository
from app.db.repositories.study import StudyRepository
from app.db.repositories.user import UserRepository
from app.db.repositories.subscription import SubscriptionRepository


class StatsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.task_repo = TaskRepository(session)
        self.reading_repo = ReadingRepository(session)
        self.study_repo = StudyRepository(session)
        self.user_repo = UserRepository(session)
        self.sub_repo = SubscriptionRepository(session)

    async def weekly_task_stats(self, user_id: int, tz: str) -> dict:
        try:
            today = date.today()
        except Exception:
            today = date.today()

        start_date = today - timedelta(days=6)
        total_tasks = 0
        done_tasks = 0

        curr = start_date
        while curr <= today:
            counts = await self.task_repo.count_by_status(user_id, curr)
            done = counts.get(TaskStatus.DONE.value, 0)
            pending = counts.get(TaskStatus.PENDING.value, 0)
            skipped = counts.get(TaskStatus.SKIPPED.value, 0)
            done_tasks += done
            total_tasks += (done + pending + skipped)
            curr += timedelta(days=1)

        total_pages = await self.reading_repo.total_pages_read(user_id)

        return {
            "period": f"{start_date.strftime('%d.%m')} - {today.strftime('%d.%m')}",
            "total_tasks": total_tasks,
            "done_tasks": done_tasks,
            "completion_rate": round((done_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0,
            "total_pages": total_pages,
        }

    async def admin_overview(self) -> dict:
        user_counts = await self.user_repo.count_by_status()
        sub_counts = await self.sub_repo.count_by_status()
        return {
            "users": user_counts,
            "subscriptions": sub_counts,
        }
