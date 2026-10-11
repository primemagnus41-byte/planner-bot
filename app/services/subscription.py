from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.utils.datetime import ensure_utc
from app.db.models.subscription import (
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
    PaymentRequest,
    PaymentRequestStatus,
)
from app.db.models.user import User, UserStatus
from app.db.repositories.subscription import (
    SubscriptionRepository,
    PaymentRequestRepository,
)


class SubscriptionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.sub_repo = SubscriptionRepository(session)
        self.pay_repo = PaymentRequestRepository(session)
        self.settings = get_settings()

    async def get_or_create_subscription(self, user: User) -> Subscription:
        sub = await self.sub_repo.get_by_user_id(user.id)
        if sub:
            return sub

        now = datetime.now(timezone.utc)
        trial_days = self.settings.trial_days
        if trial_days > 0:
            expires_at = now + timedelta(days=trial_days)
            status = SubscriptionStatus.TRIAL
            plan = SubscriptionPlan.TRIAL
            notes = f"{trial_days} kunlik bepul sinov muddati"
        else:
            expires_at = now
            status = SubscriptionStatus.EXPIRED
            plan = SubscriptionPlan.TRIAL
            notes = "Sinov muddati berilmadi"

        sub = Subscription(
            user_id=user.id,
            status=status,
            plan=plan,
            starts_at=now,
            expires_at=expires_at,
            notes=notes,
        )
        self.sub_repo.add(sub)
        await self.session.flush()
        return sub

    async def check_access(self, user: User, is_admin: bool) -> tuple[bool, str, Subscription | None]:
        """
        Returns (has_access: bool, reason: str, sub: Subscription | None)
        """
        if is_admin:
            return True, "admin", None

        if user.status == UserStatus.BANNED:
            return False, "banned", None

        sub = await self.get_or_create_subscription(user)
        now = datetime.now(timezone.utc)

        if ensure_utc(sub.expires_at) > now:
            return True, sub.status.value, sub

        if sub.status != SubscriptionStatus.EXPIRED:
            sub.status = SubscriptionStatus.EXPIRED
            await self.session.flush()

        return False, "expired", sub

    async def grant_subscription(
        self,
        user_id: int,
        plan: SubscriptionPlan,
        days: int,
        notes: str | None = None,
    ) -> Subscription:
        now = datetime.now(timezone.utc)
        sub = await self.sub_repo.get_by_user_id(user_id)
        if sub:
            sub_exp = ensure_utc(sub.expires_at)
            base_time = sub_exp if sub_exp > now else now
            sub.expires_at = base_time + timedelta(days=days)
            sub.status = SubscriptionStatus.ACTIVE
            sub.plan = plan
            if notes:
                sub.notes = notes
        else:
            sub = Subscription(
                user_id=user_id,
                status=SubscriptionStatus.ACTIVE,
                plan=plan,
                starts_at=now,
                expires_at=now + timedelta(days=days),
                notes=notes or f"{days} kunga berildi",
            )
            self.sub_repo.add(sub)
        await self.session.flush()
        return sub

    async def create_payment_request(
        self,
        user_id: int,
        plan: SubscriptionPlan,
        duration_days: int,
        receipt_info: str | None = None,
    ) -> PaymentRequest:
        req = PaymentRequest(
            user_id=user_id,
            plan=plan,
            duration_days=duration_days,
            receipt_info=receipt_info,
            status=PaymentRequestStatus.PENDING,
        )
        self.pay_repo.add(req)
        await self.session.flush()
        return req

    async def approve_payment_request(
        self, request_id: int, admin_notes: str | None = None
    ) -> tuple[PaymentRequest | None, Subscription | None]:
        req = await self.pay_repo.get(request_id)
        if not req or req.status != PaymentRequestStatus.PENDING:
            return None, None

        req.status = PaymentRequestStatus.APPROVED
        req.admin_notes = admin_notes
        sub = await self.grant_subscription(
            user_id=req.user_id,
            plan=req.plan,
            days=req.duration_days,
            notes=f"To'lov #{req.id} orqali tasdiqlandi",
        )
        await self.session.flush()
        return req, sub
