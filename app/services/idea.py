from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.idea import Idea
from app.db.repositories.idea import IdeaRepository


class IdeaNotFound(Exception):
    pass


class IdeaService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = IdeaRepository(session)

    async def add_idea(
        self,
        user_id: int,
        content: str,
        category: str | None = None,
        tag_names: list[str] | None = None,
        source: str = "text",
    ) -> Idea:
        idea = Idea(
            user_id=user_id,
            content=content.strip(),
            category=category.strip() if category else None,
            source=source,
        )
        if tag_names:
            for tag_name in tag_names:
                clean_name = tag_name.strip().lstrip("#").lower()
                if clean_name:
                    tag = await self.repo.get_or_create_tag(user_id, clean_name)
                    idea.tags.append(tag)

        self.repo.add(idea)
        await self.session.flush()
        return idea

    async def toggle_star(self, idea_id: int, user_id: int) -> Idea:
        idea = await self.repo.get_owned(idea_id, user_id)
        if not idea or idea.deleted_at is not None:
            raise IdeaNotFound
        idea.is_starred = not idea.is_starred
        return idea

    async def delete_idea(self, idea_id: int, user_id: int) -> Idea:
        idea = await self.repo.get_owned(idea_id, user_id)
        if not idea:
            raise IdeaNotFound
        idea.deleted_at = datetime.now(timezone.utc)
        return idea

    async def list_ideas(
        self,
        user_id: int,
        category: str | None = None,
        is_starred: bool | None = None,
        page: int = 1,
        page_size: int = 5,
    ) -> tuple[list[Idea], int]:
        offset = (page - 1) * page_size
        ideas = await self.repo.list_ideas(
            user_id=user_id,
            category=category,
            is_starred=is_starred,
            limit=page_size,
            offset=offset,
        )
        total = await self.repo.count_ideas(
            user_id=user_id, category=category, is_starred=is_starred
        )
        return ideas, total
