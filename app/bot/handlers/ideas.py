from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.callbacks import IdeaCb, PageCb
from app.bot.states import IdeaForm
from app.db.models.user import User
from app.services.idea import IdeaNotFound, IdeaService
from app.utils.formatting import esc
from app.utils.pagination import Paginator

router = Router(name="ideas")


@router.message(Command("ideas"))
@router.message(F.text == "💡 G'oyalar")
async def show_ideas(
    message: Message, session: AsyncSession, user: User, page: int = 1
) -> None:
    service = IdeaService(session)
    ideas, total = await service.list_ideas(user.id, page=page, page_size=4)

    if not ideas:
        await message.answer(
            "💡 <b>Sizda hali saqlangan g'oyalar yo'q.</b>\n\n"
            "Miyangizga kelgan muhim fikrlarni yozib qoldiring!",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="➕ G'oya yozish", callback_data="idea_add")]]
            ),
        )
        return

    paginator = Paginator(total, current_page=page, page_size=4)
    lines = [f"💡 <b>G'oyalar va qaydlar (jami: {total} ta):</b>\n"]
    buttons = []

    for idx, idea in enumerate(ideas, 1):
        star = "⭐️ " if idea.is_starred else ""
        lines.append(f"{idx}. {star}<b>{esc(idea.content)}</b>")

        star_btn_text = "⭐️ Olib tashlash" if idea.is_starred else "⭐️ Muhim"
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{star_btn_text} #{idx}",
                    callback_data=IdeaCb(action="star", idea_id=idea.id).pack(),
                ),
                InlineKeyboardButton(
                    text=f"🗑 O'chirish #{idx}",
                    callback_data=IdeaCb(action="delete", idea_id=idea.id).pack(),
                ),
            ]
        )

    nav_row = []
    if paginator.has_prev:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=PageCb(scope="ideas", page=page - 1).pack(),
            )
        )
    nav_row.append(InlineKeyboardButton(text=f"• {page}/{paginator.total_pages} •", callback_data="noop"))
    if paginator.has_next:
        nav_row.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=PageCb(scope="ideas", page=page + 1).pack(),
            )
        )

    buttons.append(nav_row)
    buttons.append([InlineKeyboardButton(text="➕ Yangi g'oya yozish", callback_data="idea_add")])

    await message.answer("\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(PageCb.filter(F.scope == "ideas"))
async def page_ideas_callback(
    call: CallbackQuery, callback_data: PageCb, session: AsyncSession, user: User
) -> None:
    service = IdeaService(session)
    page = callback_data.page
    ideas, total = await service.list_ideas(user.id, page=page, page_size=4)

    if not ideas:
        await call.answer()
        return

    paginator = Paginator(total, current_page=page, page_size=4)
    lines = [f"💡 <b>G'oyalar va qaydlar (jami: {total} ta):</b>\n"]
    buttons = []

    for idx, idea in enumerate(ideas, 1):
        star = "⭐️ " if idea.is_starred else ""
        lines.append(f"{idx}. {star}<b>{esc(idea.content)}</b>")

        star_btn_text = "⭐️ Olib tashlash" if idea.is_starred else "⭐️ Muhim"
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{star_btn_text} #{idx}",
                    callback_data=IdeaCb(action="star", idea_id=idea.id).pack(),
                ),
                InlineKeyboardButton(
                    text=f"🗑 O'chirish #{idx}",
                    callback_data=IdeaCb(action="delete", idea_id=idea.id).pack(),
                ),
            ]
        )

    nav_row = []
    if paginator.has_prev:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=PageCb(scope="ideas", page=page - 1).pack(),
            )
        )
    nav_row.append(InlineKeyboardButton(text=f"• {page}/{paginator.total_pages} •", callback_data="noop"))
    if paginator.has_next:
        nav_row.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=PageCb(scope="ideas", page=page + 1).pack(),
            )
        )

    buttons.append(nav_row)
    buttons.append([InlineKeyboardButton(text="➕ Yangi g'oya yozish", callback_data="idea_add")])

    await call.message.edit_text(
        "\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await call.answer()


@router.callback_query(F.data == "idea_add")
async def start_add_idea(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(IdeaForm.content)
    await call.message.answer("💡 <b>Fikr yoki g'oyangizni yozing:</b>\n\n<i>Bekor qilish: /cancel</i>")
    await call.answer()


@router.message(IdeaForm.content, F.text)
async def process_add_idea(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    service = IdeaService(session)
    idea = await service.add_idea(user.id, content=message.text)
    await state.clear()
    await message.answer(f"✅ G'oya saqlandi: <b>{esc(idea.content[:50])}</b>\n\n/ideas — ro'yxat")


@router.callback_query(IdeaCb.filter(F.action == "star"))
async def toggle_star_callback(
    call: CallbackQuery, callback_data: IdeaCb, session: AsyncSession, user: User
) -> None:
    service = IdeaService(session)
    try:
        idea = await service.toggle_star(callback_data.idea_id, user.id)
    except IdeaNotFound:
        await call.answer("G'oya topilmadi", show_alert=True)
        return

    msg = "⭐️ Muhim qilib belgilandi" if idea.is_starred else "Oddiy qilib belgilandi"
    await call.answer(msg)


@router.callback_query(IdeaCb.filter(F.action == "delete"))
async def delete_idea_callback(
    call: CallbackQuery, callback_data: IdeaCb, session: AsyncSession, user: User
) -> None:
    service = IdeaService(session)
    try:
        await service.delete_idea(callback_data.idea_id, user.id)
    except IdeaNotFound:
        await call.answer("G'oya topilmadi", show_alert=True)
        return

    await call.answer("🗑 O'chirildi")
    await call.message.delete()
