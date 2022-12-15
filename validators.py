import os
from typing import Optional, Tuple, List

from db_services import get_all_tables_name_from_db, get_all_categories_data


def admin_chat_id_validator(chat_id: int) -> Optional[True]:
    """
    Возвращает результат проверки полученного chat_id на соответствие аккаунту администратора.

    Список id админов берётся из переменной окружения. По умолчанию используется заглушка.
    """

    admin_chat_id = os.getenv("ADMIN_CHAT_ID") or "0000000000"
    list_admin_chat_id = admin_chat_id.split()

    if str(chat_id) in list_admin_chat_id:
        return True


def get_menu_validator() -> Optional[True]:
    """Проверяет, есть ли в базе данных таблица с названиями категорий меню."""

    all_tables_in_db = get_all_tables_name_from_db()
    if ("menu_categories",) in all_tables_in_db:
        return True
