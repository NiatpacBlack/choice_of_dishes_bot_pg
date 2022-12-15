import os

from dotenv import load_dotenv
from telebot import TeleBot

from db_services import (
    get_all_tables_name_from_db,
    create_table_menu_categories,
    create_table_dishes,
    get_all_categories_data,
)
from services import (
    get_start_keyboard,
    get_menu_keyboard,
    get_admin_keyboard,
    add_category_in_menu,
    add_dish_in_category,
)

load_dotenv()
bot = TeleBot(os.getenv("BOT_TOKEN"))


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Здравствуйте, {message.from_user.full_name}, выберите действие:",
        reply_markup=get_start_keyboard(),
    )


@bot.message_handler(commands=["add_category"])
def add_category(message):
    """Добавляет полученное по шаблону название категории в меню."""

    result = add_category_in_menu(message)
    bot.send_message(
        chat_id=message.chat.id,
        text=result,
    )


@bot.message_handler(commands=["add_dish"])
def add_category(message):
    result = add_dish_in_category(message=message)
    bot.send_message(
        chat_id=message.chat.id,
        text=result,
    )


@bot.callback_query_handler(func=lambda callback: callback.data == "menu")
def callback_start(callback):
    """Выводит категории меню или сообщение об его отсутствии."""

    all_tables_in_db = get_all_tables_name_from_db()

    if ("menu_categories",) not in all_tables_in_db:
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"К сожалению, меню пока не существует. Создайте его из админ-панели.",
        )
    else:
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"Выберите категорию:",
            reply_markup=get_menu_keyboard(),
        )


@bot.callback_query_handler(func=lambda callback: callback.data == "admin")
def callback_admin(callback):
    """
    Выводит функционал администратора если id чата соответствует зарегистрированному админскому id.

    Список id админов берётся из переменной окружения или непосредственно.
    """

    admin_chat_id = os.getenv("ADMIN_CHAT_ID") or "0000000000"
    list_admin_chat_id = admin_chat_id.split()

    if str(callback.message.chat.id) in list_admin_chat_id:
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"Выберите действие:",
            reply_markup=get_admin_keyboard(),
        )
    else:
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"Ваш аккаунт не имеет доступа. Обратитесь к менеджеру заведения.",
        )


@bot.callback_query_handler(func=lambda callback: callback.data == "create_menu")
def callback_create_menu(callback):
    """Создает пустые таблицы для меню в базе данных."""

    create_table_menu_categories()
    create_table_dishes()
    bot.send_message(
        chat_id=callback.message.chat.id,
        text=f"Меню успешно создано, добавьте категории и позиции блюд, чтобы увидеть меню из функционала бота.",
    )


@bot.callback_query_handler(func=lambda callback: callback.data == "add_category")
def callback_add_category(callback):
    """Сообщает пользователю в ответном сообщении действия, которые нужно сделать, чтобы добавить новую категорию."""

    bot.send_message(
        chat_id=callback.message.chat.id,
        text=f"Что-бы добавить категорию отправьте боту сообщение:\n<i>'/add_category название_категории'</i>",
        parse_mode="html",
    )


@bot.callback_query_handler(func=lambda callback: callback.data == "add_dish")
def callback_add_dish(callback):
    """Сообщает пользователю в ответном сообщении действия, которые нужно сделать, чтобы добавить новое блюдо."""

    categories_string = "\n".join(
        map(lambda el: str(el)[5:-2], get_all_categories_data())
    )
    bot.send_message(
        chat_id=callback.message.chat.id,
        text=f"Что-бы добавить блюдо в категорию отправьте боту сообщение:"
        f"\n<i>'/add_dish название_категории название_блюда цена описание</i>'"
        f"\n\n<b>Обратите внимание, что название категории или блюда нужно писать через нижнее подчеркивание"
        f" вместо пробела, иначе блюдо не будет добавлено!</b>"
        f"\n\nСписок доступных категорий:"
        f"\n<i>{categories_string if categories_string else 'Доступных категорий нет'}</i>",
        parse_mode="html",
    )


@bot.callback_query_handler(func=lambda callback: callback.data == "back_to_start")
def callback_create_menu(callback):
    """Возвращает пользователя на начальное меню."""

    bot.send_message(
        chat_id=callback.message.chat.id,
        text=f"Выберите действие:",
        reply_markup=get_start_keyboard(),
    )


if __name__ == "__main__":
    bot.polling(non_stop=True, interval=0)
