import enum
from datetime import date, datetime
from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class BookStatus(str, enum.Enum):
    PLANNED = "planned"
    READING = "reading"
    FINISHED = "finished"
    DROPPED = "dropped"


class Book(Base, TimestampMixin):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(500))
    author: Mapped[str | None] = mapped_column(String(255), default=None)

    total_pages: Mapped[int | None] = mapped_column(default=None)
    current_page: Mapped[int] = mapped_column(default=0)

    status: Mapped[BookStatus] = mapped_column(default=BookStatus.PLANNED, index=True)
    started_at: Mapped[datetime | None] = mapped_column(default=None)
    finished_at: Mapped[datetime | None] = mapped_column(default=None)

    sessions: Mapped[list["ReadingSession"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )
    review: Mapped["Review | None"] = relationship(
        back_populates="book", uselist=False, cascade="all, delete-orphan"
    )


class ReadingSession(Base):
    __tablename__ = "reading_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    read_date: Mapped[date] = mapped_column(index=True)
    pages: Mapped[int] = mapped_column(default=0)
    minutes: Mapped[int | None] = mapped_column(default=None)

    book: Mapped[Book] = relationship(back_populates="sessions")


class Review(Base, TimestampMixin):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), unique=True)
    content: Mapped[str] = mapped_column(Text)
    rating: Mapped[int | None] = mapped_column(default=None)

    book: Mapped[Book] = relationship(back_populates="review")
