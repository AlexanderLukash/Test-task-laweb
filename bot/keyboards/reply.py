from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def create_start_keyboard(is_admin: bool) -> ReplyKeyboardMarkup:
    # Основні кнопки, які відображаються для всіх користувачів
    buttons = [
        [KeyboardButton(text="🤵 Профіль")],
        [KeyboardButton(text="🚀 Відправка заявок")],
        [
            KeyboardButton(text="🧑‍💻 Підтримка"),
            KeyboardButton(text="🔘 Whitelist"),
        ],
    ]

    # Додаткова кнопка для адміністратора
    if is_admin:
        buttons.append([KeyboardButton(text="💠 Змінити статус")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="👇 Натискайте на кнопки",
        selective=True,
    )


cancel_button = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="❌ Відмінити",
            ),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="👇 Введіть ID або натисніть на кнопку, щоб відмінити",
    selective=True,
)

change_status_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="demo",
            ),
        ],
        [
            KeyboardButton(
                text="unlim",
            ),
        ],
        [
            KeyboardButton(
                text="admin",
            ),
        ],
        [
            KeyboardButton(
                text="❌ Відмінити",
            ),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="👇 Введіть ID або натисніть на кнопку, щоб відмінити",
    selective=True,
)

whitelist_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Додати домен",
            ),
        ],
        [
            KeyboardButton(
                text="Список доменів",
            ),
        ],
        [
            KeyboardButton(
                text="Повернутися в головне меню",
            ),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="👇 Натискайте на кнопки",
    one_time_keyboard=True,
)

return_white_list_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Повернутися назад",
            ),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)


def generate_domain_keyboard(domains: list[str]) -> ReplyKeyboardMarkup:
    """Створює клавіатуру для видалення доменів з whitelist."""
    domain_buttons = [[KeyboardButton(text=domain)] for domain in domains]
    domain_buttons.append([KeyboardButton(text="Повернутися назад")])

    return ReplyKeyboardMarkup(
        keyboard=domain_buttons,
        resize_keyboard=True,
        one_time_keyboard=True,
        selective=True,
    )


applications_main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Запустити відправку 🚀",
            ),
        ],
        [
            KeyboardButton(
                text="Активні сесії 🕜",
            ),
        ],
        [
            KeyboardButton(
                text="Повернутися в головне меню",
            ),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="👇 Натискайте на кнопки",
    one_time_keyboard=True,
    selective=True,
)

applications_start_cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Скасувати відправку ❌",
            ),
        ],
        [
            KeyboardButton(
                text="В меню заявок",
            ),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="👇 Натискайте на кнопки",
    one_time_keyboard=True,
    selective=True,
)

# Кнопки для вибору частоти
frequency_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Без затримки 🚀",
            ),
        ],
        [
            KeyboardButton(
                text="1 заявка в 10 секунд ⏳",
            ),
        ],
        [
            KeyboardButton(
                text="1 заявка в 10 хвилин ⌛",
            ),
        ],
        [
            KeyboardButton(
                text="1 заявка в 60 хвилин ⌛",
            ),
        ],
        [
            KeyboardButton(
                text="Скасувати відправку ❌",
            ),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)


def create_duration_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(
                text="1 хвилина ⏳",
            ),
        ],
        [
            KeyboardButton(
                text="15 хвилин ⏳",
            ),
        ],
        [
            KeyboardButton(
                text="30 хвилин ⏳",
            ),
        ],
        [
            KeyboardButton(
                text="1 година ⏳",
            ),
        ],
        [
            KeyboardButton(
                text="3 години ⏳",
            ),
        ],
        [
            KeyboardButton(
                text="Скасувати відправку ❌",
            ),
        ],
    ]
    if is_admin:
        keyboard.append(
            [
                KeyboardButton(
                    text="Необмежено ⏳",
                ),
            ],
        )
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
