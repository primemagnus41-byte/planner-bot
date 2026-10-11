from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.reading import Book, BookStatus, ReadingSession, Review
from app.db.repositories.reading import ReadingRepository


class BookNotFound(Exception):
    pass


class ReadingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ReadingRepository(session)

    async def add_book(
        self,
        user_id: int,
        title: str,
        author: str | None = None,
        total_pages: int | None = None,
    ) -> Book:
        book = Book(
            user_id=user_id,
            title=title.strip(),
            author=author.strip() if author else None,
            total_pages=total_pages,
            status=BookStatus.PLANNED,
        )
        self.repo.add(book)
        await self.session.flush()
        return book

    async def start_reading(self, book_id: int, user_id: int) -> Book:
        book = await self.repo.get_owned(book_id, user_id)
        if not book:
            raise BookNotFound
        book.status = BookStatus.READING
        if not book.started_at:
            book.started_at = datetime.now(timezone.utc)
        return book

    async def log_session(
        self,
        user_id: int,
        book_id: int,
        pages: int,
        read_date: date,
        minutes: int | None = None,
    ) -> tuple[Book, ReadingSession]:
        book = await self.repo.get_owned(book_id, user_id)
        if not book:
            raise BookNotFound
        book.current_page += pages
        if book.status == BookStatus.PLANNED:
            book.status = BookStatus.READING
            book.started_at = datetime.now(timezone.utc)
        if book.total_pages and book.current_page >= book.total_pages:
            book.status = BookStatus.FINISHED
            book.finished_at = datetime.now(timezone.utc)

        session_obj = await self.repo.add_session(
            user_id, book_id, read_date, pages, minutes
        )
        await self.session.flush()
        return book, session_obj

    async def finish_book(
        self,
        book_id: int,
        user_id: int,
        review_content: str | None = None,
        rating: int | None = None,
    ) -> Book:
        book = await self.repo.get_with_details(book_id, user_id)
        if not book:
            raise BookNotFound
        book.status = BookStatus.FINISHED
        book.finished_at = datetime.now(timezone.utc)
        if book.total_pages:
            book.current_page = book.total_pages

        if review_content:
            if book.review:
                book.review.content = review_content
                book.review.rating = rating
            else:
                review = Review(
                    user_id=user_id,
                    book_id=book_id,
                    content=review_content,
                    rating=rating,
                )
                book.review = review
                self.session.add(review)
        await self.session.flush()
        return book

    async def list_books(
        self, user_id: int, status: BookStatus | None = None
    ) -> list[Book]:
        return await self.repo.list_books(user_id, status)
