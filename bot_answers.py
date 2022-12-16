from collections import namedtuple

TrueFalseAnswer = namedtuple('TrueFalseAnswer', 'answer false_answer')

cb_menu_answer = TrueFalseAnswer(
    answer="Выберите действие:",
    false_answer="К сожалению, меню пока не существует. Создайте его из админ-панели.",
)

cb_admin_answer = TrueFalseAnswer(
    answer="Выберите действие:",
    false_answer="Ваш аккаунт не имеет доступа. Обратитесь к менеджеру заведения.",
)

cb_create_menu_answer = TrueFalseAnswer(
    answer="Меню успешно создано, добавьте категории и позиции блюд, чтобы увидеть меню из функционала бота.",
    false_answer=None,
)

cb_add_category_answer = TrueFalseAnswer(
    answer="Что-бы добавить категорию отправьте боту сообщение:\n<i>'/add_category название_категории'</i>",
    false_answer=None,
)

cb_add_dish_answer = TrueFalseAnswer(
    answer=f"Что-бы добавить блюдо в категорию отправьте боту сообщение:"
           f"\n<i>'/add_dish название_категории название_блюда цена описание</i>'"
           f"\n\n<b>Обратите внимание, что название категории или блюда нужно писать через нижнее подчеркивание"
           f" вместо пробела, иначе блюдо не будет добавлено!</b>"
           f"\n\nСписок доступных категорий:\n",
    false_answer=None,
)

cb_back_to_start_answer = TrueFalseAnswer(
    answer="Выберите действие:",
    false_answer=None,
)

add_category_answer = TrueFalseAnswer(
    answer="Блюдо успешно добавлено в категорию.",
    false_answer="Переданное сообщение на соответствует форме.",
)
