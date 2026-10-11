from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.services.stats import StatsService
from app.utils.formatting import progress_bar

router = Router(name="stats")


@router.message(Command("stats"))
@router.message(F.text == "📊 Statistika")
async def show_stats(message: Message, session: AsyncSession, user: User) -> None:
    service = StatsService(session)
    tz = user.settings.timezone if user.settings else "Asia/Tashkent"
    stats = await service.weekly_task_stats(user.id, tz)

    total = stats["total_tasks"]
    done = stats["done_tasks"]
    rate = stats["completion_rate"]
    bar = progress_bar(done, total or 1, width=10)

    text = (
        f"📊 <b>Haftalik hisobot ({stats['period']}):</b>\n\n"
        f"📋 <b>Rejalar ijrosi:</b>\n"
        f"[{bar}] {done}/{total} ta ({rate}%)\n\n"
        f"📚 <b>O'qilgan kitob betlari:</b> {stats['total_pages']} bet\n\n"
        "<i>Intizom — erkinlik garovidir!</i>"
    )
    await message.answer(text)
