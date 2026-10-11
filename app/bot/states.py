from aiogram.fsm.state import State, StatesGroup


class TaskForm(StatesGroup):
    title = State()
    plan_date = State()
    time = State()
    priority = State()


class BookForm(StatesGroup):
    title = State()
    author = State()
    total_pages = State()


class ReadingSessionForm(StatesGroup):
    pages = State()
    minutes = State()


class ReviewForm(StatesGroup):
    rating = State()
    content = State()


class StudyForm(StatesGroup):
    subject_name = State()
    topic_title = State()
    notes = State()


class IdeaForm(StatesGroup):
    content = State()
    category = State()
    tags = State()


class AdminGrantForm(StatesGroup):
    user_id = State()
    days = State()
