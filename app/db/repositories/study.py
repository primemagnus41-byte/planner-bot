from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.db.models.study import Subject, Topic, SrsCard, TopicStatus
from app.db.repositories.base import BaseRepository


class StudyRepository(BaseRepository[Topic]):
    model = Topic

    async def list_subjects(self, user_id: int) -> list[Subject]:
        stmt = (
            select(Subject)
            .where(Subject.user_id == user_id)
            .order_by(Subject.name)
        )
        return list(await self.session.scalars(stmt))

    async def get_subject_owned(self, subject_id: int, user_id: int) -> Subject | None:
        stmt = select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
        return await self.session.scalar(stmt)

    async def list_topics(
        self, user_id: int, subject_id: int | None = None
    ) -> list[Topic]:
        stmt = (
            select(Topic)
            .options(selectinload(Topic.card), selectinload(Topic.subject))
            .where(Topic.user_id == user_id)
        )
        if subject_id is not None:
            stmt = stmt.where(Topic.subject_id == subject_id)
        stmt = stmt.order_by(Topic.id.desc())
        return list(await self.session.scalars(stmt))

    async def list_due_cards(
        self, user_id: int, due_before: datetime
    ) -> list[SrsCard]:
        stmt = (
            select(SrsCard)
            .options(selectinload(SrsCard.topic))
            .where(SrsCard.user_id == user_id, SrsCard.due_at <= due_before)
            .order_by(SrsCard.due_at)
        )
        return list(await self.session.scalars(stmt))

    async def count_due_cards(self, user_id: int, due_before: datetime) -> int:
        stmt = (
            select(func.count(SrsCard.id))
            .where(SrsCard.user_id == user_id, SrsCard.due_at <= due_before)
        )
        return int(await self.session.scalar(stmt) or 0)
