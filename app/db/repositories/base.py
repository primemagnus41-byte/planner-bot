from typing import Any, Generic, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, pk: Any) -> ModelT | None:
        return await self.session.get(self.model, pk)

    async def get_owned(self, pk: Any, user_id: int) -> ModelT | None:
        """Har doim user_id bilan tekshirish — IDOR himoyasi."""
        stmt = select(self.model).where(
            self.model.id == pk, self.model.user_id == user_id
        )
        return await self.session.scalar(stmt)

    def add(self, obj: ModelT) -> ModelT:
        self.session.add(obj)
        return obj
