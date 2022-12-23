from telebot import types

from db_services import get_all_categories_data, get_all_tables_name_from_db, get_dishes_from_category_where


def get_start_keyboard():
    """Возвращает кнопки выпадающие при старте бота."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Меню", callback_data="menu"))
    keyboard.add(
        types.InlineKeyboardButton(text="Панель администратора", callback_data="admin")
    )
    return keyboard


def get_menu_keyboard():
    """Возвращает кнопки с названиями категорий, если таковые имеются."""

    categories_data = get_all_categories_data()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text="Назад", callback_data="back_to_start")
    )
    if categories_data:
        for category_id, category_name in categories_data:
            keyboard.add(
                types.InlineKeyboardButton(
                    text=category_name, callback_data="category_" + str(category_id)
                )
            )
    return keyboard


def get_admin_keyboard():
    """Возвращает кнопки с функциями администратора."""

    keyboard = types.InlineKeyboardMarkup()
    all_tables_in_db = get_all_tables_name_from_db()

    keyboard.add(
        types.InlineKeyboardButton(text="Назад", callback_data="back_to_start")
    )
    if ("menu_categories",) not in all_tables_in_db:
        keyboard.add(
            types.InlineKeyboardButton(text="Создать меню", callback_data="create_menu")
        )
    else:
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
        keyboard.add(
            types.InlineKeyboardButton(
                text="Топ 3 самых популярных блюда", callback_data="top_dishes_report"
            )
        )
        keyboard.add(
            types.InlineKeyboardButton(
                text="Топ 3 самых активных пользователя",
                callback_data="top_users_report",
            )
        )
        keyboard.add(
            types.InlineKeyboardButton(
                text="Последние полученные сообщения",
                callback_data="last_messages_report",
            )
        )

    return keyboard


def get_dishes_keyboard(category_id):
    """Возвращает кнопки соответствующие позициям из конкретной категории меню."""

    keyboard = types.InlineKeyboardMarkup()
    all_dishes_from_category = get_dishes_from_category_where(category_id)

    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back_to_menu"))

    if all_dishes_from_category:
        for dish_id, dish_name in all_dishes_from_category:
            keyboard.add(
                types.InlineKeyboardButton(
                    text=dish_name, callback_data="dish_" + str(dish_id)
                )
            )
    return keyboard


def back_to_dishes_button(category_id: int):
    """Возвращает кнопку для перехода блюдам соответствующей категории меню."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text="Назад", callback_data=f"category_{category_id}"
        )
    )
    return keyboard
