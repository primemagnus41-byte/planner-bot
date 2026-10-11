import enum
from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class SubscriptionStatus(str, enum.Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "canceled"


class SubscriptionPlan(str, enum.Enum):
    TRIAL = "trial"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    LIFETIME = "lifetime"


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        default=SubscriptionStatus.TRIAL, index=True
    )
    plan: Mapped[SubscriptionPlan] = mapped_column(
        default=SubscriptionPlan.TRIAL
    )
    starts_at: Mapped[datetime] = mapped_column()
    expires_at: Mapped[datetime] = mapped_column(index=True)
    notes: Mapped[str | None] = mapped_column(String(255), default=None)

    user: Mapped["User"] = relationship("User", back_populates="subscription")


class PaymentRequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PaymentRequest(Base, TimestampMixin):
    __tablename__ = "payment_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    plan: Mapped[SubscriptionPlan]
    duration_days: Mapped[int]
    status: Mapped[PaymentRequestStatus] = mapped_column(
        default=PaymentRequestStatus.PENDING, index=True
    )
    receipt_info: Mapped[str | None] = mapped_column(Text, default=None)
    admin_notes: Mapped[str | None] = mapped_column(String(255), default=None)
