from typing import Tuple, List

from telebot import types

from db_services import (
    get_all_categories_data,
    get_all_tables_name_from_db,
    insert_category_in_table_menu_categories,
    get_category_id_where_category_name,
    insert_dish_in_dishes_table,
)


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
    return keyboard


def add_category_in_menu(message) -> str:
    """
    Достает из полученного сообщения название категории и добавляет его в таблицу с категориями меню.

    Если сообщение не имеет данных о категории, возвращает текстовую ошибку.
    """

    list_message_words = message.text.split()
    if len(list_message_words) != 1:
        category_name = " ".join(list_message_words[1:])
        insert_category_in_table_menu_categories(category_name)
        return "Категория успешно создана!"
    return "Вы не передали название категории."


def add_dish_in_category(message) -> str:
    """
    Достает из полученного сообщения название категории и блюда и добавляет его в соответствующую категорию меню.

    Если сообщение не имеет данных о категории или блюде, возвращает текстовую ошибку.
    """

    list_message_words = message.text.split()[1:]
    parameters = {"category": "", "dish": "", "price": "", "description": ""}

    if 5 > len(list_message_words) >= 3:
        for index, word in enumerate(list_message_words):
            parameters[list(parameters.keys())[index]] = " ".join(word.split("_"))

        category_id = get_category_id_where_category_name(
            category_name=parameters["category"]
        )

        if category_id and parameters["price"].isdigit():

            insert_dish_in_dishes_table(
                dish_name=parameters["dish"],
                category_id=str(category_id),
                price=parameters["price"],
                description=parameters["description"],
            )

            return f"Блюдо успешно добавлено в категорию {parameters['category']}."

    return "Переданное сообщение на соответствует форме."


def get_nice_categories_format(categories_data: List[Tuple[str, ...]]) -> str:
    """Преобразует список с данными категорий меню в удобочитаемый строчный формат."""

    return "\n".join(map(lambda category_data: category_data[1], categories_data))
