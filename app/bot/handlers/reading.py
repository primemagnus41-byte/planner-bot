from datetime import date
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.callbacks import BookCb
from app.bot.states import BookForm, ReadingSessionForm
from app.db.models.reading import BookStatus
from app.db.models.user import User
from app.services.reading import BookNotFound, ReadingService
from app.utils.formatting import esc, progress_bar

router = Router(name="reading")


@router.message(Command("books"))
@router.message(F.text == "📚 Kitoblar")
@router.callback_query(F.data == "nav_books")
async def show_books(event: Message | CallbackQuery, session: AsyncSession, user: User) -> None:
    service = ReadingService(session)
    books = await service.list_books(user.id)

    if not books:
        text = (
            "📚 <b>Sizda hali kitoblar ro'yxati yo'q.</b>\n\n"
            "O'qiyotgan yoki rejalashtirgan kitobingizni qo'shing!"
        )
        markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="➕ Kitob qo'shish", callback_data="book_add")]]
        )
    else:
        lines = ["📚 <b>Kitoblaringiz ro'yxati:</b>\n"]
        buttons = []
        for b in books:
            status_emoji = "📖" if b.status == BookStatus.READING else ("✅" if b.status == BookStatus.FINISHED else "📌")
            bar = progress_bar(b.current_page, b.total_pages or 100, width=8) if b.total_pages else ""
            pages_info = f"({b.current_page}/{b.total_pages} bet)" if b.total_pages else f"({b.current_page} bet)"
            lines.append(f"{status_emoji} <b>{esc(b.title)}</b> {pages_info}\n   [{bar}]")

            if b.status != BookStatus.FINISHED:
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"➕ O'qilgan bet: {b.title[:20]}",
                            callback_data=BookCb(action="read", book_id=b.id).pack(),
                        )
                    ]
                )

        buttons.append([InlineKeyboardButton(text="➕ Yangi kitob qo'shish", callback_data="book_add")])
        text = "\n".join(lines)
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    if isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    else:
        await event.message.edit_text(text, reply_markup=markup)
        await event.answer()


@router.callback_query(F.data == "book_add")
async def start_add_book(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BookForm.title)
    await call.message.answer("📖 <b>Kitob nomini kiriting:</b>\n\n<i>Bekor qilish: /cancel</i>")
    await call.answer()


@router.message(BookForm.title, F.text)
async def process_book_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(BookForm.total_pages)
    await message.answer("📄 <b>Kitob necha betdan iborat?</b> (Masalan: 320)\n\n<i>Agar bilmasangiz: 0</i>")


@router.message(BookForm.total_pages, F.text)
async def process_book_pages(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    data = await state.get_data()
    title = data["title"]
    try:
        pages = int(message.text.strip())
        pages = pages if pages > 0 else None
    except ValueError:
        pages = None

    service = ReadingService(session)
    book = await service.add_book(user.id, title=title, total_pages=pages)
    await state.clear()
    await message.answer(f"✅ Kitob qo'shildi: <b>{esc(book.title)}</b>\n\n/books — kitoblar ro'yxati")


@router.callback_query(BookCb.filter(F.action == "read"))
async def start_log_pages(
    call: CallbackQuery, callback_data: BookCb, state: FSMContext
) -> None:
    await state.set_state(ReadingSessionForm.pages)
    await state.update_data(book_id=callback_data.book_id)
    await call.message.answer(
        "📖 <b>Bugun necha bet o'qidingiz?</b> (Masalan: 15)\n\n<i>Bekor qilish: /cancel</i>"
    )
    await call.answer()


@router.message(ReadingSessionForm.pages, F.text)
async def process_log_pages(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    try:
        pages = int(message.text.strip())
        if pages <= 0:
            raise ValueError
    except ValueError:
        await message.answer("⚠️ Iltimos, musbat son kiriting (masalan: 20).")
        return

    data = await state.get_data()
    book_id = data["book_id"]
    service = ReadingService(session)

    try:
        book, _ = await service.log_session(
            user_id=user.id,
            book_id=book_id,
            pages=pages,
            read_date=date.today(),
        )
    except BookNotFound:
        await message.answer("⚠️ Kitob topilmadi.")
        await state.clear()
        return

    await state.clear()
    finished_msg = "\n🎉 <b>Tabriklaymiz, kitobni o'qib tugatdingiz!</b>" if book.status == BookStatus.FINISHED else ""
    await message.answer(
        f"✅ <b>{pages} bet</b> qayd qilindi!\n"
        f"📖 <b>{esc(book.title)}:</b> jami {book.current_page} bet o'qildi.{finished_msg}\n\n"
        "/books — kitoblar ro'yxati"
    )
