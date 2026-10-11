import enum
from datetime import datetime, time
from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class UserStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    BANNED = "banned"
    BLOCKED_BOT = "blocked_bot"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram ID
    username: Mapped[str | None] = mapped_column(String(64), default=None)
    full_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[UserStatus] = mapped_column(default=UserStatus.PENDING, index=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(default=None)

    settings: Mapped["UserSettings"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    subscription: Mapped["Subscription | None"] = relationship(
        "Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class UserSettings(Base, TimestampMixin):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Tashkent")
    locale: Mapped[str] = mapped_column(String(5), default="uz")

    morning_time: Mapped[time | None] = mapped_column(default=time(7, 30))
    evening_time: Mapped[time | None] = mapped_column(default=time(21, 0))
    reading_time: Mapped[time | None] = mapped_column(default=time(20, 0))
    review_time: Mapped[time | None] = mapped_column(default=time(10, 0))

    reminders_enabled: Mapped[bool] = mapped_column(default=True)

    user: Mapped[User] = relationship(back_populates="settings")
