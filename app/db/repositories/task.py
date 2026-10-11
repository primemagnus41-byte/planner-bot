from datetime import date
from sqlalchemy import func, select

from app.db.models.task import Task, TaskStatus
from app.db.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    model = Task

    async def list_for_day(self, user_id: int, day: date) -> list[Task]:
        stmt = (
            select(Task)
            .where(
                Task.user_id == user_id,
                Task.plan_date == day,
                Task.deleted_at.is_(None),
            )
            .order_by(Task.due_at.nulls_last(), Task.priority.desc(), Task.id)
        )
        return list(await self.session.scalars(stmt))

    async def count_by_status(self, user_id: int, day: date) -> dict[str, int]:
        stmt = (
            select(Task.status, func.count())
            .where(
                Task.user_id == user_id,
                Task.plan_date == day,
                Task.deleted_at.is_(None),
            )
            .group_by(Task.status)
        )
        rows = await self.session.execute(stmt)
        return {s.value if hasattr(s, "value") else str(s): c for s, c in rows}

    async def carry_over(self, user_id: int, from_day: date, to_day: date) -> int:
        """Bajarilmagan vazifalarni ertangi kunga ko'chirish."""
        tasks = await self.list_for_day(user_id, from_day)
        moved = 0
        for t in tasks:
            if t.status == TaskStatus.PENDING:
                t.plan_date = to_day
                moved += 1
        return moved
