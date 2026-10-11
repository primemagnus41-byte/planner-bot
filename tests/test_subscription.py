import pytest
from app.db.models.subscription import SubscriptionPlan, SubscriptionStatus
from app.services.subscription import SubscriptionService
from app.services.user import UserService


@pytest.mark.asyncio
async def test_subscription_trial_and_grant(session):
    user_service = UserService(session)
    user, _ = await user_service.get_or_create(99999, "Subscriber", "subscriber")

    sub_service = SubscriptionService(session)

    # Check access - receives trial
    has_access, reason, sub = await sub_service.check_access(user, is_admin=False)
    assert has_access is True
    assert reason == "trial"
    assert sub.status == SubscriptionStatus.TRIAL

    # Admin grant 30 days
    updated_sub = await sub_service.grant_subscription(
        user_id=user.id,
        plan=SubscriptionPlan.MONTHLY,
        days=30,
        notes="Admin test grant",
    )
    assert updated_sub.status == SubscriptionStatus.ACTIVE
    assert updated_sub.plan == SubscriptionPlan.MONTHLY


@pytest.mark.asyncio
async def test_naive_datetime_handling(session):
    user_service = UserService(session)
    user, _ = await user_service.get_or_create(88888, "NaiveUser", "naiveuser")

    sub_service = SubscriptionService(session)
    sub = await sub_service.get_or_create_subscription(user)
    # Simulate SQLite returning offset-naive datetime
    sub.expires_at = sub.expires_at.replace(tzinfo=None)

    has_access, reason, checked_sub = await sub_service.check_access(user, is_admin=False)
    assert has_access is True
