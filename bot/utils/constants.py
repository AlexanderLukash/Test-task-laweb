# Функція для привітального повідомлення
def start_message() -> str:
    text = (
        "⚡️ Привіт! За допомогою цього боту ти можеш відправити заявки на будь які сайти з формою\n"
        "💎 Ми маємо різні режими з вибором тривалості та швидкості відправки заявок\n"
        "💡 Всі поля, випадаючі списки, галочки в формі на сайтах заповнюються автоматично\n"
        "🔥 Тисни кнопку нижче та запускай відправку!"
    )

    return text


# Функція для повідомлення профілю користувача
def profile_message(
    user_id: int,
    translated_status: str,
    days_since_registration: int,
    total_applications_sent: int,
) -> str:
    text = (
        f"<b>🤵 Ваш профіль</b>\n\n"
        f"📊 Ваш статус: {translated_status}\n"
        f"🪪 Ваш Telegram ID: <code>{user_id}</code>\n"
        f"🥇 Ми разом вже {days_since_registration} днів\n"
        f"📩 Загалом надіслано заявок: {total_applications_sent}"
    )

    return text
