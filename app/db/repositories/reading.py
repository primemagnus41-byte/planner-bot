from datetime import date
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.db.models.reading import Book, BookStatus, ReadingSession, Review
from app.db.repositories.base import BaseRepository


class ReadingRepository(BaseRepository[Book]):
    model = Book

    async def list_books(
        self, user_id: int, status: BookStatus | None = None
    ) -> list[Book]:
        stmt = select(Book).where(Book.user_id == user_id)
        if status:
            stmt = stmt.where(Book.status == status)
        stmt = stmt.order_by(Book.id.desc())
        return list(await self.session.scalars(stmt))

    async def get_with_details(self, book_id: int, user_id: int) -> Book | None:
        stmt = (
            select(Book)
            .options(selectinload(Book.sessions), selectinload(Book.review))
            .where(Book.id == book_id, Book.user_id == user_id)
        )
        return await self.session.scalar(stmt)

    async def add_session(
        self, user_id: int, book_id: int, read_date: date, pages: int, minutes: int | None = None
    ) -> ReadingSession:
        session_obj = ReadingSession(
            user_id=user_id, book_id=book_id, read_date=read_date, pages=pages, minutes=minutes
        )
        self.session.add(session_obj)
        return session_obj

    async def total_pages_read(self, user_id: int) -> int:
        stmt = select(func.coalesce(func.sum(ReadingSession.pages), 0)).where(
            ReadingSession.user_id == user_id
        )
        return int(await self.session.scalar(stmt) or 0)
