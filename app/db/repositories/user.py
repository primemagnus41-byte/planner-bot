from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.models.user import User, UserSettings, UserStatus
from app.db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_with_settings(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .options(selectinload(User.settings), selectinload(User.subscription))
            .where(User.id == user_id)
        )
        return await self.session.scalar(stmt)

    async def list_approved(self) -> list[User]:
        stmt = (
            select(User)
            .options(selectinload(User.settings), selectinload(User.subscription))
            .where(User.status == UserStatus.APPROVED)
        )
        return list(await self.session.scalars(stmt))

    async def list_pending(self) -> list[User]:
        stmt = select(User).where(User.status == UserStatus.PENDING)
        return list(await self.session.scalars(stmt))

    async def count_by_status(self) -> dict[str, int]:
        stmt = select(User.status, func.count()).group_by(User.status)
        rows = await self.session.execute(stmt)
        return {status.value if hasattr(status, "value") else str(status): count for status, count in rows}
