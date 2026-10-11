from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.callbacks import TaskCb
from app.bot.keyboards.inline import task_undo_keyboard, tasks_keyboard
from app.bot.states import TaskForm
from app.db.models.user import User
from app.services.task import TaskNotFound, TaskService
from app.utils.formatting import esc, format_task_list

router = Router(name="tasks")


@router.message(Command("plan"))
@router.message(F.text == "📋 Reja")
async def show_plan(message: Message, session: AsyncSession, user: User) -> None:
    service = TaskService(session)
    tz = user.settings.timezone if user.settings else "Asia/Tashkent"
    summary = await service.day_summary(user.id, tz)
    if not summary["tasks"]:
        await message.answer(
            "📋 <b>Bugungi reja ro'yxati bo'sh.</b>\n\n"
            "Yangi vazifa qo'shish uchun: ➕ Vazifa yoki /add"
        )
        return
    await message.answer(
        format_task_list(summary),
        reply_markup=tasks_keyboard(summary["tasks"]),
    )


@router.callback_query(F.data == "nav_plan")
async def show_plan_callback(call: CallbackQuery, session: AsyncSession, user: User) -> None:
    service = TaskService(session)
    tz = user.settings.timezone if user.settings else "Asia/Tashkent"
    summary = await service.day_summary(user.id, tz)
    if not summary["tasks"]:
        await call.message.answer(
            "📋 <b>Bugungi reja ro'yxati bo'sh.</b>\n\n"
            "Yangi vazifa qo'shish uchun: ➕ Vazifa yoki /add"
        )
        await call.answer()
        return
    await call.message.edit_text(
        format_task_list(summary),
        reply_markup=tasks_keyboard(summary["tasks"]),
    )
    await call.answer()


@router.message(Command("add"))
@router.message(F.text == "➕ Vazifa")
@router.callback_query(F.data == "nav_add_task")
async def add_task_start(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TaskForm.title)
    prompt = (
        "✏️ <b>Yangi vazifa nomini kiriting:</b>\n\n"
        "<i>Bekor qilish uchun: /cancel</i>"
    )
    if isinstance(event, Message):
        await event.answer(prompt)
    else:
        await event.message.answer(prompt)
        await event.answer()


@router.message(TaskForm.title, F.text)
async def add_task_title(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    service = TaskService(session)
    tz = user.settings.timezone if user.settings else "Asia/Tashkent"
    task = await service.add(user.id, message.text, tz)
    await state.clear()
    await message.answer(f"✅ Vazifa qo'shildi: <b>{esc(task.title)}</b>\n\n/plan — barcha rejalar")


@router.callback_query(TaskCb.filter(F.action == "done"))
async def task_done(
    call: CallbackQuery, callback_data: TaskCb, session: AsyncSession, user: User
) -> None:
    service = TaskService(session)
    try:
        await service.complete(callback_data.task_id, user.id)
    except TaskNotFound:
        await call.answer("Vazifa topilmadi", show_alert=True)
        return

    await call.answer("✅ Bajarildi deb belgilandi")
    tz = user.settings.timezone if user.settings else "Asia/Tashkent"
    summary = await service.day_summary(user.id, tz)
    await call.message.edit_text(
        format_task_list(summary), reply_markup=tasks_keyboard(summary["tasks"])
    )


@router.callback_query(TaskCb.filter(F.action == "skip"))
async def task_skip(
    call: CallbackQuery, callback_data: TaskCb, session: AsyncSession, user: User
) -> None:
    service = TaskService(session)
    try:
        await service.skip(callback_data.task_id, user.id)
    except TaskNotFound:
        await call.answer("Vazifa topilmadi", show_alert=True)
        return

    await call.answer("⚪️ O'tkazib yuborildi")
    tz = user.settings.timezone if user.settings else "Asia/Tashkent"
    summary = await service.day_summary(user.id, tz)
    await call.message.edit_text(
        format_task_list(summary), reply_markup=tasks_keyboard(summary["tasks"])
    )


@router.callback_query(TaskCb.filter(F.action == "delete"))
async def task_delete(
    call: CallbackQuery, callback_data: TaskCb, session: AsyncSession, user: User
) -> None:
    service = TaskService(session)
    try:
        task = await service.soft_delete(callback_data.task_id, user.id)
    except TaskNotFound:
        await call.answer("Vazifa topilmadi", show_alert=True)
        return

    await call.answer("🗑 O'chirildi")
    await call.message.answer(
        f"🗑 <b>O'chirildi:</b> {esc(task.title)}",
        reply_markup=task_undo_keyboard(task.id),
    )
    tz = user.settings.timezone if user.settings else "Asia/Tashkent"
    summary = await service.day_summary(user.id, tz)
    await call.message.edit_text(
        format_task_list(summary), reply_markup=tasks_keyboard(summary["tasks"])
    )


@router.callback_query(TaskCb.filter(F.action == "restore"))
async def task_restore(
    call: CallbackQuery, callback_data: TaskCb, session: AsyncSession, user: User
) -> None:
    service = TaskService(session)
    try:
        task = await service.restore(callback_data.task_id, user.id)
    except TaskNotFound:
        await call.answer("Vazifa topilmadi", show_alert=True)
        return

    await call.answer("↩️ Qayta tiklandi")
    await call.message.edit_text(f"✅ Qayta tiklandi: <b>{esc(task.title)}</b>")
