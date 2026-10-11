from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.task import Priority, Task, TaskStatus
from app.db.repositories.task import TaskRepository


class TaskNotFound(Exception):
    pass


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = TaskRepository(session)

    @staticmethod
    def today_for(tz: str) -> date:
        try:
            return datetime.now(ZoneInfo(tz)).date()
        except Exception:
            return datetime.now(ZoneInfo("Asia/Tashkent")).date()

    async def add(
        self,
        user_id: int,
        title: str,
        tz: str,
        plan_date: date | None = None,
        local_time: str | None = None,      # "09:00"
        priority: Priority = Priority.NORMAL,
    ) -> Task:
        day = plan_date or self.today_for(tz)
        due_at = None
        if local_time:
            hh, mm = map(int, local_time.split(":"))
            local_dt = datetime.combine(
                day, datetime.min.time(), tzinfo=ZoneInfo(tz)
            ).replace(hour=hh, minute=mm)
            due_at = local_dt.astimezone(timezone.utc)

        task = Task(
            user_id=user_id,
            title=title.strip(),
            plan_date=day,
            due_at=due_at,
            priority=priority,
        )
        self.repo.add(task)
        await self.session.flush()
        return task

    async def complete(
        self, task_id: int, user_id: int, note: str | None = None
    ) -> Task:
        task = await self.repo.get_owned(task_id, user_id)
        if task is None or task.deleted_at is not None:
            raise TaskNotFound
        task.status = TaskStatus.DONE
        task.completed_at = datetime.now(timezone.utc)
        if note:
            task.note = note
        return task

    async def skip(self, task_id: int, user_id: int) -> Task:
        task = await self.repo.get_owned(task_id, user_id)
        if task is None or task.deleted_at is not None:
            raise TaskNotFound
        task.status = TaskStatus.SKIPPED
        return task

    async def soft_delete(self, task_id: int, user_id: int) -> Task:
        task = await self.repo.get_owned(task_id, user_id)
        if task is None:
            raise TaskNotFound
        task.deleted_at = datetime.now(timezone.utc)
        return task

    async def restore(self, task_id: int, user_id: int) -> Task:
        """UNDO — 'O'chirildi ↩️ Qaytarish' tugmasi uchun."""
        task = await self.repo.get_owned(task_id, user_id)
        if task is None:
            raise TaskNotFound
        task.deleted_at = None
        return task

    async def day_summary(
        self, user_id: int, tz: str, day: date | None = None
    ) -> dict:
        day = day or self.today_for(tz)
        tasks = await self.repo.list_for_day(user_id, day)
        return {
            "date": day,
            "tasks": tasks,
            "done": [t for t in tasks if t.status == TaskStatus.DONE],
            "skipped": [t for t in tasks if t.status == TaskStatus.SKIPPED],
            "pending": [t for t in tasks if t.status == TaskStatus.PENDING],
        }

    async def carry_over_pending(
        self, user_id: int, tz: str
    ) -> int:
        today = self.today_for(tz)
        yesterday = today - timedelta(days=1)
        return await self.repo.carry_over(user_id, yesterday, today)
