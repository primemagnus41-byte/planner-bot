from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.keyboards.callbacks import BookCb, IdeaCb, PageCb, StudyCb, SubCb, TaskCb
from app.db.models.task import Task, TaskStatus


def tasks_keyboard(tasks: list[Task]) -> InlineKeyboardMarkup:
    buttons = []
    for t in tasks:
        if t.status == TaskStatus.PENDING:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"✅ {t.title[:25]}",
                        callback_data=TaskCb(action="done", task_id=t.id).pack(),
                    ),
                    InlineKeyboardButton(
                        text="⏩",
                        callback_data=TaskCb(action="skip", task_id=t.id).pack(),
                    ),
                    InlineKeyboardButton(
                        text="🗑",
                        callback_data=TaskCb(action="delete", task_id=t.id).pack(),
                    ),
                ]
            )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def task_undo_keyboard(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="↩️ Qaytarish (Undo)",
                    callback_data=TaskCb(action="restore", task_id=task_id).pack(),
                )
            ]
        ]
    )


def srs_review_keyboard(card_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="😵 Esimda yo'q (0)",
                    callback_data=StudyCb(action="rate", card_id=card_id, quality=0).pack(),
                ),
                InlineKeyboardButton(
                    text="😐 Qiyin (3)",
                    callback_data=StudyCb(action="rate", card_id=card_id, quality=3).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🙂 Yaxshi (4)",
                    callback_data=StudyCb(action="rate", card_id=card_id, quality=4).pack(),
                ),
                InlineKeyboardButton(
                    text="😎 Oson (5)",
                    callback_data=StudyCb(action="rate", card_id=card_id, quality=5).pack(),
                ),
            ],
        ]
    )


def subscription_keyboard(admin_username: str) -> InlineKeyboardMarkup:
    clean_username = admin_username.lstrip("@")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Tariflar bilan tanishish",
                    callback_data=SubCb(action="plans").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬 Adminga murojaat qilish",
                    url=f"https://t.me/{clean_username}",
                )
            ],
        ]
    )


def pagination_keyboard(
    scope: str, current_page: int, has_prev: bool, has_next: bool
) -> InlineKeyboardMarkup:
    nav_row = []
    if has_prev:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=PageCb(scope=scope, page=current_page - 1).pack(),
            )
        )
    nav_row.append(
        InlineKeyboardButton(
            text=f"• {current_page} •",
            callback_data="noop",
        )
    )
    if has_next:
        nav_row.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=PageCb(scope=scope, page=current_page + 1).pack(),
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=[nav_row])
