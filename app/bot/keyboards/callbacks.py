from aiogram.filters.callback_data import CallbackData


class TaskCb(CallbackData, prefix="task"):
    action: str  # done | skip | delete | restore
    task_id: int


class BookCb(CallbackData, prefix="book"):
    action: str  # read | finish | detail
    book_id: int


class StudyCb(CallbackData, prefix="study"):
    action: str  # rate | next
    card_id: int
    quality: int = 0


class IdeaCb(CallbackData, prefix="idea"):
    action: str  # star | delete
    idea_id: int


class PageCb(CallbackData, prefix="page"):
    scope: str  # ideas | books | topics
    page: int
    tag: str = ""


class SubCb(CallbackData, prefix="sub"):
    action: str  # buy | info | plans


class AdminCb(CallbackData, prefix="adm"):
    action: str  # grant | ban | unban | list_users
    target_id: int = 0
