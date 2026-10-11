from datetime import datetime, timezone
from sqlalchemy import select, func

from app.db.models.subscription import (
    Subscription,
    SubscriptionStatus,
    SubscriptionPlan,
    PaymentRequest,
    PaymentRequestStatus,
)
from app.db.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    model = Subscription

    async def get_by_user_id(self, user_id: int) -> Subscription | None:
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        return await self.session.scalar(stmt)

    async def list_active(self) -> list[Subscription]:
        now = datetime.now(timezone.utc)
        stmt = select(Subscription).where(
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]),
            Subscription.expires_at > now,
        )
        return list(await self.session.scalars(stmt))

    async def count_by_status(self) -> dict[str, int]:
        stmt = select(Subscription.status, func.count()).group_by(Subscription.status)
        rows = await self.session.execute(stmt)
        return {status.value if hasattr(status, "value") else str(status): count for status, count in rows}


class PaymentRequestRepository(BaseRepository[PaymentRequest]):
    model = PaymentRequest

    async def get_pending_for_user(self, user_id: int) -> PaymentRequest | None:
        stmt = (
            select(PaymentRequest)
            .where(
                PaymentRequest.user_id == user_id,
                PaymentRequest.status == PaymentRequestStatus.PENDING,
            )
            .order_by(PaymentRequest.id.desc())
        )
        return await self.session.scalar(stmt)

    async def list_pending(self, limit: int = 50) -> list[PaymentRequest]:
        stmt = (
            select(PaymentRequest)
            .where(PaymentRequest.status == PaymentRequestStatus.PENDING)
            .order_by(PaymentRequest.id.desc())
            .limit(limit)
        )
        return list(await self.session.scalars(stmt))
