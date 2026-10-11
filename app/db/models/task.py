import enum
from datetime import date, datetime
from sqlalchemy import BigInteger, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    DONE = "done"
    SKIPPED = "skipped"


class Priority(int, enum.Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    title: Mapped[str] = mapped_column(String(500))
    note: Mapped[str | None] = mapped_column(Text, default=None)

    plan_date: Mapped[date] = mapped_column(index=True)
    due_at: Mapped[datetime | None] = mapped_column(default=None)
    priority: Mapped[Priority] = mapped_column(default=Priority.NORMAL)

    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.PENDING, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(default=None)

    rrule: Mapped[str | None] = mapped_column(String(255), default=None)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"), default=None)

    deleted_at: Mapped[datetime | None] = mapped_column(default=None)

    __table_args__ = (
        Index("ix_tasks_user_date_status", "user_id", "plan_date", "status"),
    )
