import re
from datetime import datetime
from typing import Tuple

import pytz as pytz
from telebot import TeleBot

from bot_answers import (
    cb_admin_answer,
    cb_create_menu_answer,
    cb_add_category_answer,
    cb_add_dish_answer,
    cb_back_to_start_answer,
    cb_menu_answer,
    add_category_answer,
    cb_dishes_in_category_answer,
    cb_back_to_menu_answer,
)
from config import BOT_TOKEN
from db_services import (
    create_table_menu_categories,
    create_table_dishes,
    get_all_categories_data,
    get_dish_parameters,
    create_table_selection_dishes,
    add_dish_selection_in_selection_dishes_table,
    create_table_last_messages,
    add_message_in_last_messages_table,
)
from services import (
    get_start_keyboard,
    get_menu_keyboard,
    get_admin_keyboard,
    add_category_in_menu,
    add_dish_in_category,
    get_nice_categories_format,
    get_dishes_keyboard,
    back_to_dishes_button,
    get_most_popular_dishes_report,
    get_most_popular_users_report,
    get_last_messages_report,
)
from validators import (
    admin_chat_id_validator,
    get_menu_validator,
    allowable_length_validator,
)

bot = TeleBot(BOT_TOKEN)
last_message_data = []


def rewrite_last_message(func):
    """Декоратор, созданный для перезаписи последнего сообщения."""

    def wrapper(*args, **kwargs):
        global last_message_data

        if last_message_data:
            bot.delete_message(*last_message_data)

        last_message_data = func(*args, **kwargs)

    return wrapper


@bot.message_handler(commands=["start"])
@rewrite_last_message
def start(message) -> Tuple[int, int]:
    last_message = bot.send_message(
        chat_id=message.chat.id,
        text=f"Здравствуйте, {message.from_user.full_name}, выберите действие:",
        reply_markup=get_start_keyboard(),
    )
    return message.chat.id, last_message.id


@bot.message_handler(commands=["add_category"])
@rewrite_last_message
def add_category(message) -> Tuple[int, int]:
    """Добавляет полученное по шаблону название категории в меню."""

    validation_result = allowable_length_validator(message.text, 60)
    result = add_category_in_menu(message) if validation_result else cb_add_category_answer.false_answer
    last_message = bot.send_message(
        chat_id=message.chat.id,
        text=result,
        reply_markup=get_admin_keyboard() if validation_result else None,
    )
    return message.chat.id, last_message.id


@bot.message_handler(commands=["add_dish"])
@rewrite_last_message
def add_dish(message) -> Tuple[int, int]:
    """Пытается добавить переданное блюдо из сообщения в меню. Отправляет пользователю ответ о результате добавления."""

    result = add_dish_in_category(message=message)
    last_message = bot.send_message(
        chat_id=message.chat.id,
        text=add_category_answer.answer if result else add_category_answer.false_answer,
        reply_markup=get_admin_keyboard(),
    )
    return message.chat.id, last_message.id


@bot.message_handler(content_types=["text"])
def handle_text_message(message) -> None:
    """Отлавливает все текстовые сообщения переданные боту и записывает их в таблицу базы данных."""

    add_message_in_last_messages_table(message.text)


@bot.callback_query_handler(func=lambda callback: callback.data == "menu")
@rewrite_last_message
def callback_menu(callback) -> Tuple[int, int]:
    """Выводит категории меню или сообщение об его отсутствии."""

    validation_result = get_menu_validator()
    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_menu_answer.answer
        if validation_result
        else cb_menu_answer.false_answer,
        reply_markup=get_menu_keyboard() if validation_result else None,
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "admin")
@rewrite_last_message
def callback_admin(callback) -> Tuple[int, int]:
    """Выводит функционал администратора если id чата соответствует зарегистрированному админскому id."""

    validation_result = admin_chat_id_validator(callback.message.chat.id)

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_admin_answer.answer
        if validation_result
        else cb_admin_answer.false_answer,
        reply_markup=get_admin_keyboard() if validation_result else None,
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "create_menu")
@rewrite_last_message
def callback_create_menu(callback) -> Tuple[int, int]:
    """При нажатии кнопки 'Создать меню' создает пустые таблицы для меню в бд и уведомит об этом пользователя."""

    create_table_menu_categories()
    create_table_dishes()
    create_table_selection_dishes()
    create_table_last_messages()

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_create_menu_answer.answer,
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "add_category")
@rewrite_last_message
def callback_add_category(callback) -> Tuple[int, int]:
    """Сообщает пользователю в ответном сообщении действия, которые нужно сделать, чтобы добавить новую категорию."""

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_add_category_answer.answer,
        parse_mode="html",
        reply_markup=get_admin_keyboard(),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "add_dish")
@rewrite_last_message
def callback_add_dish(callback) -> Tuple[int, int]:
    """
    Сообщает пользователю в ответном сообщении действия, которые нужно сделать, чтобы добавить новое блюдо.

    В ответном сообщении присутствуют текущие доступные категории из меню, чтобы пользователь понимал с чем работать.
    """

    categories_data = get_all_categories_data()
    categories_text = (
        get_nice_categories_format(categories_data)
        if categories_data
        else "Доступных категорий нет"
    )

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_add_dish_answer.answer + f"<i>{categories_text}</i>",
        parse_mode="html",
        reply_markup=get_admin_keyboard(),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "back_to_start")
@rewrite_last_message
def callback_back_to_start(callback) -> Tuple[int, int]:
    """Отправляет пользователю кнопки стартового меню."""

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_back_to_start_answer.answer,
        reply_markup=get_start_keyboard(),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "back_to_menu")
@rewrite_last_message
def callback_back_to_menu(callback) -> Tuple[int, int]:
    """Отправляет пользователю кнопки с категориями меню."""

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_back_to_menu_answer.answer,
        reply_markup=get_menu_keyboard(),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: re.match(r"category_", callback.data))
@rewrite_last_message
def callback_dishes_in_category(callback) -> Tuple[int, int]:
    """Получает id категории из коллбека, и отображает все блюда этой категории."""

    category_id = callback.data.replace("category_", "")

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=cb_dishes_in_category_answer.answer,
        reply_markup=get_dishes_keyboard(category_id),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: re.match(r"dish_", callback.data))
@rewrite_last_message
def callback_parameters_from_dish(callback) -> Tuple[int, int]:
    """Отображает пользователю полные данные о блюде, получая его id из коллбека."""

    dish_id = callback.data.replace("dish_", "")
    dish_parameters = get_dish_parameters(dish_id)

    add_dish_selection_in_selection_dishes_table(
        user_name=f"{callback.from_user.first_name} {callback.from_user.last_name or ''}",
        dish_id=dish_id,
        date=datetime.now(pytz.timezone("Europe/Minsk")),
    )

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=f"Подробности о товаре <b>{dish_parameters[1]}</b>:\n\n"
             f"<b>Цена:</b> {dish_parameters[3]}р.\n\n"
             f'{"<b>Описание:</b> " + dish_parameters[4] if dish_parameters[4] else ""}\n\n'
             f'{"Активен" if dish_parameters[5] else "Нет в продаже"}',
        parse_mode="html",
        reply_markup=back_to_dishes_button(dish_parameters[2]),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "top_dishes_report")
@rewrite_last_message
def callback_top_dishes(callback) -> Tuple[int, int]:
    """Отправляет пользователю информацию о топе самых популярных блюд."""

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=get_most_popular_dishes_report(count=3),
        parse_mode="html",
        reply_markup=get_admin_keyboard(),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(func=lambda callback: callback.data == "top_users_report")
@rewrite_last_message
def callback_top_users(callback) -> Tuple[int, int]:
    """Отправляет пользователю информацию о топе самых популярных блюд."""

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=get_most_popular_users_report(count=3),
        parse_mode="html",
        reply_markup=get_admin_keyboard(),
    )
    return callback.message.chat.id, last_message.id


@bot.callback_query_handler(
    func=lambda callback: callback.data == "last_messages_report"
)
@rewrite_last_message
def callback_last_messages(callback) -> Tuple[int, int]:
    """Отправляет пользователю информацию о 100 последних сообщениях полученных ботом от пользователей."""

    last_message = bot.send_message(
        chat_id=callback.message.chat.id,
        text=get_last_messages_report(count=100),
        parse_mode="html",
        reply_markup=get_admin_keyboard(),
    )
    return callback.message.chat.id, last_message.id


if __name__ == "__main__":
    bot.polling(non_stop=True, interval=0)
