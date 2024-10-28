import logging

from aiogram import Router
from aiogram.types import Message


other_user_router = Router()
logger = logging.getLogger(__name__)


# Обробник повідомлення, коли користувач обирає опцію "Підтримка"
@other_user_router.message(lambda message: message.text == "🧑‍💻 Підтримка")
async def support_handler(message: Message):
    logger.info(f"User {message.from_user.id} звернувся до підтримки")
    await message.answer("✉️ Для звʼязку з нами звертайтеся до...")
