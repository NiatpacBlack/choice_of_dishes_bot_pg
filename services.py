from telebot import types


def get_start_keyboard():
    """Возвращает кнопки выпадающие при старте бота."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Меню", callback_data="menu"))
    keyboard.add(
        types.InlineKeyboardButton(text="Панель администратора", callback_data="admin")
    )
    return keyboard


def get_menu_keyboard():
    """Возвращает кнопки с названиями категорий."""

    categories = ...  # get_all_categories()
    keyboard = types.InlineKeyboardMarkup()
    for category in categories:
        keyboard.add(types.InlineKeyboardButton(text=category, callback_data=category))

    return keyboard


def get_admin_keyboard():
    """Возвращает кнопки с функциями администратора."""

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text="Добавить категорию", callback_data="add_category"
        )
    )
    keyboard.add(
        types.InlineKeyboardButton(
            text="Добавить блюдо в категорию", callback_data="add_dish"
        )
    )
    return keyboard
