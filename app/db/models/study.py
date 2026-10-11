import enum
from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class TopicStatus(str, enum.Enum):
    NEW = "new"
    LEARNING = "learning"
    MASTERED = "mastered"


class Subject(Base, TimestampMixin):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(128))

    topics: Mapped[list["Topic"]] = relationship(back_populates="subject")


class Topic(Base, TimestampMixin):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[int | None] = mapped_column(ForeignKey("subjects.id", ondelete="SET NULL"), default=None)

    title: Mapped[str] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text, default=None)
    status: Mapped[TopicStatus] = mapped_column(default=TopicStatus.NEW)

    subject: Mapped[Subject | None] = relationship(back_populates="topics")
    card: Mapped["SrsCard | None"] = relationship(
        back_populates="topic", uselist=False, cascade="all, delete-orphan"
    )


class SrsCard(Base):
    __tablename__ = "srs_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), unique=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)

    ease_factor: Mapped[float] = mapped_column(default=2.5)
    interval_days: Mapped[int] = mapped_column(default=0)
    repetitions: Mapped[int] = mapped_column(default=0)
    due_at: Mapped[datetime] = mapped_column(index=True)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(default=None)
    lapses: Mapped[int] = mapped_column(default=0)

    topic: Mapped[Topic] = relationship(back_populates="card")
