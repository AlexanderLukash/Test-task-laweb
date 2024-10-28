import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.users.users import UserManager

from bot.keyboards.reply import create_start_keyboard
from bot.utils.constants import start_message


start_user_router = Router()
logger = logging.getLogger(__name__)


@start_user_router.message(CommandStart())
@start_user_router.message(lambda message: message.text == "Повернутися в головне меню")
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    logger.info(f"Користувач {message.from_user.id} ввів /start.")
    manager: UserManager = UserManager()

    manager.register_user(
        user_id=message.from_user.id,
    )

    await message.answer(
        text=start_message(),
        reply_markup=create_start_keyboard(is_admin=False),
    )
