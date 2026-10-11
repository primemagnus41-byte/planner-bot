from datetime import datetime
from sqlalchemy import select

from app.db.models.reminder import Reminder, ReminderKind
from app.db.repositories.base import BaseRepository


class ReminderRepository(BaseRepository[Reminder]):
    model = Reminder

    async def list_due(self, now: datetime, limit: int = 100) -> list[Reminder]:
        stmt = (
            select(Reminder)
            .where(
                Reminder.sent_at.is_(None),
                Reminder.fire_at <= now,
                Reminder.attempts < 5,
            )
            .order_by(Reminder.fire_at)
            .limit(limit)
        )
        return list(await self.session.scalars(stmt))

    async def find_by_dedup(
        self, user_id: int, kind: ReminderKind, dedup_key: str
    ) -> Reminder | None:
        stmt = select(Reminder).where(
            Reminder.user_id == user_id,
            Reminder.kind == kind,
            Reminder.dedup_key == dedup_key,
        )
        return await self.session.scalar(stmt)
