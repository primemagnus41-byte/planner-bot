from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User, UserSettings, UserStatus
from app.db.repositories.user import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = UserRepository(session)

    async def get_or_create(
        self, tg_id: int, full_name: str, username: str | None
    ) -> tuple[User, bool]:
        user = await self.repo.get_with_settings(tg_id)
        if user:
            user.full_name = full_name
            user.username = username
            user.last_seen_at = datetime.now(timezone.utc)
            return user, False

        user = User(
            id=tg_id,
            full_name=full_name,
            username=username,
            status=UserStatus.PENDING,
            last_seen_at=datetime.now(timezone.utc),
        )
        settings = UserSettings(user_id=tg_id)
        user.settings = settings
        self.repo.add(user)
        await self.session.flush()
        return user, True

    async def set_status(self, user: User, status: UserStatus) -> None:
        user.status = status
        await self.session.flush()

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.repo.get_with_settings(user_id)
