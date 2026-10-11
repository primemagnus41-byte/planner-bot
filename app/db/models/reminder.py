import enum
from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReminderKind(str, enum.Enum):
    MORNING = "morning"
    EVENING = "evening"
    READING = "reading"
    SRS_REVIEW = "srs_review"
    TASK_DUE = "task_due"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"


class Reminder(Base):
    """OUTBOX: Yuborilishi kerak bo'lgan har bir eslatma shu yerda saqlanadi."""
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    kind: Mapped[ReminderKind]
    payload: Mapped[str | None] = mapped_column(Text, default=None)       # JSON

    fire_at: Mapped[datetime] = mapped_column(index=True)                 # UTC
    sent_at: Mapped[datetime | None] = mapped_column(default=None)
    attempts: Mapped[int] = mapped_column(default=0)
    last_error: Mapped[str | None] = mapped_column(String(500), default=None)

    dedup_key: Mapped[str] = mapped_column(String(128))                   # "morning:2026-09-25"

    __table_args__ = (
        UniqueConstraint("user_id", "kind", "dedup_key", name="uq_reminder_dedup"),
        Index("ix_reminders_pending", "sent_at", "fire_at"),
    )
