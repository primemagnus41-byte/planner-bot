from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.callbacks import StudyCb
from app.bot.keyboards.inline import srs_review_keyboard
from app.bot.states import StudyForm
from app.db.models.user import User
from app.services.study import CardNotFound, StudyService
from app.utils.formatting import esc

router = Router(name="study")


@router.message(Command("study"))
@router.message(F.text == "🧠 Dars & SM-2")
@router.callback_query(F.data == "nav_study")
async def show_study_session(
    event: Message | CallbackQuery, session: AsyncSession, user: User
) -> None:
    service = StudyService(session)
    due_cards = await service.get_due_cards(user.id)

    if not due_cards:
        text = (
            "🎉 <b>Ajoyib! Bugun takrorlanadigan mavzular yo'q.</b>\n\n"
            "Barcha o'tilgan darslar o'z vaqtida mustahkamlangan.\n"
            "Yangi mavzu qo'shish uchun pastdagi tugmani bosing."
        )
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➕ Yangi mavzu qo'shish", callback_data="study_add")]
            ]
        )
    else:
        card = due_cards[0]
        topic = card.topic
        text = (
            f"🧠 <b>Takrorlash sessiyasi ({len(due_cards)} ta mavzu qoldi):</b>\n\n"
            f"📌 <b>Mavzu:</b> {esc(topic.title)}\n"
        )
        if topic.notes:
            text += f"📝 <b>Qaydlar/Savol:</b>\n<i>{esc(topic.notes)}</i>\n\n"
        text += "Xotirangizni qay darajada esladingiz?"
        markup = srs_review_keyboard(card.id)

    if isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    else:
        await event.message.edit_text(text, reply_markup=markup)
        await event.answer()


@router.callback_query(StudyCb.filter(F.action == "rate"))
async def process_study_rate(
    call: CallbackQuery, callback_data: StudyCb, session: AsyncSession, user: User
) -> None:
    service = StudyService(session)
    try:
        card = await service.review_card(
            card_id=callback_data.card_id,
            user_id=user.id,
            quality=callback_data.quality,
        )
    except CardNotFound:
        await call.answer("Mavzu topilmadi", show_alert=True)
        return

    due_date_str = card.due_at.strftime("%d.%m.%Y")
    await call.answer(f"Qabul qilindi. Keyingi takrorlash: {due_date_str}")
    # Keyingi kartani ko'rsatish
    await show_study_session(call, session, user)


@router.callback_query(F.data == "study_add")
async def start_add_topic(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(StudyForm.topic_title)
    await call.message.answer(
        "🧠 <b>Yodlash/takrorlash uchun mavzu nomini kiriting:</b>\n\n<i>Bekor qilish: /cancel</i>"
    )
    await call.answer()


@router.message(StudyForm.topic_title, F.text)
async def process_topic_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(StudyForm.notes)
    await message.answer(
        "📝 <b>Mavzu bo'yicha qisqa qayd, ta'rif yoki savolni kiriting:</b>\n\n"
        "<i>(Agar qayd shart bo'lmasa: 'yo'q' deb yozing)</i>"
    )


@router.message(StudyForm.notes, F.text)
async def process_topic_notes(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    data = await state.get_data()
    title = data["title"]
    notes = message.text.strip()
    if notes.lower() in ["yo'q", "yoq", "none", "-"]:
        notes = None

    service = StudyService(session)
    topic = await service.add_topic(user_id=user.id, title=title, notes=notes)
    await state.clear()
    await message.answer(
        f"✅ Mavzu SM-2 tizimiga qo'shildi: <b>{esc(topic.title)}</b>\n\n"
        "/study — takrorlash sessiyasini boshlash"
    )
