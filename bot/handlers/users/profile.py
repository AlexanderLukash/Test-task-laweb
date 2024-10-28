import logging
from datetime import datetime

from aiogram import Router
from aiogram.types import Message

from services.users.users import UserManager

from bot.utils.constants import profile_message


profile_users_router = Router()
logger = logging.getLogger(__name__)


# Обробник повідомлення, коли користувач обирає опцію "Профіль"
@profile_users_router.message(lambda message: message.text == "🤵 Профіль")
async def profile_handler(message: Message):
    logger.info(f"Користувач {message.from_user.id} переглянув свій профіль")
    user_manager = UserManager()
    user_data = user_manager.get_user_info(message.from_user.id)
    if user_data:
        registration_date = user_data.get("registration_date")
        status = user_data.get("status", "N/A")
        total_applications_sent = user_data.get("applications_sent")
        days_since_registration = (
            datetime.now() - datetime.fromisoformat(registration_date)
        ).days
        await message.answer(
            text=profile_message(
                user_id=message.from_user.id,
                translated_status=status,
                total_applications_sent=total_applications_sent,
                days_since_registration=days_since_registration,
            ),
        )
    else:
        await message.answer("⚠️ Ви не зареєстровані. Напишіть боту /start")
