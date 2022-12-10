import os

from dotenv import load_dotenv
from telebot import TeleBot

from db_services import get_all_tables_name_from_db, create_table_menu_categories, create_table_dishes
from services import get_start_keyboard, get_menu_keyboard, get_admin_keyboard

load_dotenv()
bot = TeleBot(os.getenv("BOT_TOKEN"))


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        f"Здравствуйте, {message.from_user.full_name}, выберите действие:",
        reply_markup=get_start_keyboard(),
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
    """Выводит функционал администратора при проверке chat_id."""

    if callback.message.chat.id not in [
        int(chat_id) for chat_id in os.getenv("ADMIN_CHAT_ID").split()
    ]:
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"Ваш аккаунт не имеет доступа. Обратитесь к менеджеру заведения.",
        )
    else:
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=f"Выберите действие:",
            reply_markup=get_admin_keyboard(),
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
    pass


@bot.callback_query_handler(func=lambda callback: callback.data == "add_dish")
def callback_add_dish(callback):
    pass


if __name__ == "__main__":
    bot.polling(non_stop=True, interval=0)
