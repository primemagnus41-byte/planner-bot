from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User

router = Router(name="settings")


@router.message(Command("settings"))
@router.message(F.text == "⚙️ Sozlamalar")
async def show_settings(message: Message, user: User) -> None:
    settings = user.settings
    status_reminders = "Yoqilgan ✅" if settings.reminders_enabled else "O'chirilgan ❌"

    text = (
        "⚙️ <b>Foydalanuvchi sozlamalari:</b>\n\n"
        f"🌐 <b>Vaqt mintaqasi (Timezone):</b> {settings.timezone}\n"
        f"⏰ <b>Kunlik eslatmalar:</b> {status_reminders}\n"
        f"🌅 Ertalabki eslatma: {settings.morning_time.strftime('%H:%M') if settings.morning_time else 'Yo\'q'}\n"
        f"🌙 Kechki eslatma: {settings.evening_time.strftime('%H:%M') if settings.evening_time else 'Yo\'q'}\n"
        f"📚 Mutolaa eslatmasi: {settings.reading_time.strftime('%H:%M') if settings.reading_time else 'Yo\'q'}\n"
    )

    toggle_btn_text = "🔕 Eslatmalarni o'chirish" if settings.reminders_enabled else "🔔 Eslatmalarni yoqish"
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=toggle_btn_text, callback_data="toggle_reminders")]
        ]
    )
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data == "toggle_reminders")
async def toggle_reminders(call: CallbackQuery, session: AsyncSession, user: User) -> None:
    settings = user.settings
    settings.reminders_enabled = not settings.reminders_enabled
    await session.flush()

    status = "yoqildi ✅" if settings.reminders_enabled else "o'chirildi 🔕"
    await call.answer(f"Eslatmalar {status}")

    status_reminders = "Yoqilgan ✅" if settings.reminders_enabled else "O'chirilgan ❌"
    text = (
        "⚙️ <b>Foydalanuvchi sozlamalari:</b>\n\n"
        f"🌐 <b>Vaqt mintaqasi:</b> {settings.timezone}\n"
        f"⏰ <b>Kunlik eslatmalar:</b> {status_reminders}\n"
        f"🌅 Ertalabki eslatma: {settings.morning_time.strftime('%H:%M') if settings.morning_time else 'Yo\'q'}\n"
        f"🌙 Kechki eslatma: {settings.evening_time.strftime('%H:%M') if settings.evening_time else 'Yo\'q'}\n"
        f"📚 Mutolaa eslatmasi: {settings.reading_time.strftime('%H:%M') if settings.reading_time else 'Yo\'q'}\n"
    )
    toggle_btn_text = "🔕 Eslatmalarni o'chirish" if settings.reminders_enabled else "🔔 Eslatmalarni yoqish"
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=toggle_btn_text, callback_data="toggle_reminders")]
        ]
    )
    await call.message.edit_text(text, reply_markup=markup)
