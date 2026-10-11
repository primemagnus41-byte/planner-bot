from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.db.models.idea import Idea, Tag
from app.db.repositories.base import BaseRepository


class IdeaRepository(BaseRepository[Idea]):
    model = Idea

    async def list_ideas(
        self,
        user_id: int,
        category: str | None = None,
        is_starred: bool | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Idea]:
        stmt = (
            select(Idea)
            .options(selectinload(Idea.tags))
            .where(Idea.user_id == user_id, Idea.deleted_at.is_(None))
        )
        if category:
            stmt = stmt.where(Idea.category == category)
        if is_starred is not None:
            stmt = stmt.where(Idea.is_starred == is_starred)
        stmt = stmt.order_by(Idea.id.desc()).limit(limit).offset(offset)
        return list(await self.session.scalars(stmt))

    async def count_ideas(
        self,
        user_id: int,
        category: str | None = None,
        is_starred: bool | None = None,
    ) -> int:
        stmt = (
            select(func.count(Idea.id))
            .where(Idea.user_id == user_id, Idea.deleted_at.is_(None))
        )
        if category:
            stmt = stmt.where(Idea.category == category)
        if is_starred is not None:
            stmt = stmt.where(Idea.is_starred == is_starred)
        return int(await self.session.scalar(stmt) or 0)

    async def get_or_create_tag(self, user_id: int, name: str) -> Tag:
        stmt = select(Tag).where(Tag.user_id == user_id, Tag.name == name)
        tag = await self.session.scalar(stmt)
        if not tag:
            tag = Tag(user_id=user_id, name=name)
            self.session.add(tag)
            await self.session.flush()
        return tag
