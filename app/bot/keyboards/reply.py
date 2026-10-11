from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text="📋 Reja"),
            KeyboardButton(text="➕ Vazifa"),
        ],
        [
            KeyboardButton(text="📚 Kitoblar"),
            KeyboardButton(text="🧠 Dars & SM-2"),
        ],
        [
            KeyboardButton(text="💡 G'oyalar"),
            KeyboardButton(text="📊 Statistika"),
        ],
        [
            KeyboardButton(text="💎 Obuna"),
            KeyboardButton(text="⚙️ Sozlamalar"),
        ],
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="👑 Admin panel")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
