from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot import texts
from app.bot.keyboards.reply import main_menu_keyboard
from app.config import get_settings
from app.db.models.user import User
from app.services.subscription import SubscriptionService
from app.services.task import TaskService

router = Router(name="common")
settings = get_settings()


@router.message(CommandStart())
async def cmd_start(
    message: Message, state: FSMContext, session: AsyncSession, user: User, is_admin: bool
) -> None:
    await state.clear()
    sub_service = SubscriptionService(session)
    sub = await sub_service.get_or_create_subscription(user)

    welcome_msg = texts.WELCOME_START.format(name=user.full_name)
    if sub and sub.status.value == "trial":
        exp_str = sub.expires_at.strftime("%d.%m.%Y")
        welcome_msg += f"\n\n🎁 <b>Sizga {settings.trial_days} kunlik bepul sinov berildi!</b> (Muddati: {exp_str})"

    # Carry over pending tasks from yesterday if any
    task_service = TaskService(session)
    tz = user.settings.timezone if user.settings else "Asia/Tashkent"
    moved = await task_service.carry_over_pending(user.id, tz)
    if moved > 0:
        welcome_msg += f"\n\n📌 Kechagi kundan bajarilmagan <b>{moved} ta</b> vazifa bugungi rejaga o'tkazildi."

    await message.answer(welcome_msg, reply_markup=main_menu_keyboard(is_admin))


@router.message(Command("cancel"))
@router.message(F.text.casefold() == "bekor qilish")
async def cmd_cancel(message: Message, state: FSMContext, is_admin: bool) -> None:
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Hech qanday faol amal yo'q.", reply_markup=main_menu_keyboard(is_admin))
        return

    await state.clear()
    await message.answer(texts.CANCELLED, reply_markup=main_menu_keyboard(is_admin))


@router.message(Command("help"))
async def cmd_help(message: Message, is_admin: bool) -> None:
    help_text = (
        "💡 <b>Botdan foydalanish bo'yicha qo'llanma:</b>\n\n"
        "📋 <b>Reja:</b> Kunlik rejangizni ko'rish va boshqarish\n"
        "➕ <b>Vazifa:</b> Yangi reja yoki vazifa qo'shish\n"
        "📚 <b>Kitoblar:</b> O'qiyotgan kitoblaringiz sahifalarini qayd etish\n"
        "🧠 <b>Dars & SM-2:</b> Spaced Repetition (oraliqli takrorlash) orqali mavzularni eslab qolish\n"
        "💡 <b>G'oyalar:</b> Muhim fikr va xotiralarni tez saqlash\n"
        "📊 <b>Statistika:</b> Haftalik samaradorlik hisoboti\n"
        "💎 <b>Obuna:</b> Tariflar va hisob holati\n\n"
        "<i>Har qanday jarayonni bekor qilish uchun: /cancel</i>"
    )
    await message.answer(help_text, reply_markup=main_menu_keyboard(is_admin))
