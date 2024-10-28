import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.users.users import UserManager

from bot.filters.admin import AdminFilter
from bot.keyboards.reply import (
    cancel_button,
    change_status_keyboard,
    create_start_keyboard,
)
from bot.utils.states import ChangeUserStatusState


admin_commands_router = Router()
admin_commands_router.message.filter(AdminFilter())
logger = logging.getLogger(__name__)


@admin_commands_router.message(lambda message: message.text == "💠 Змінити статус")
async def change_status_handler(message: Message, state: FSMContext):
    logger.info(f"Користувач {message.from_user.id} натиснув кнопку 'Змінити статус'")
    await state.set_state(ChangeUserStatusState.id)
    await message.answer(
        text="👤 Введіть Telegram ID користувача, якому хочете змінити статус:",
        reply_markup=cancel_button,
    )


@admin_commands_router.message(lambda message: message.text == "❌ Відмінити")
async def cancel_handler(message: Message, state: FSMContext):
    logger.info(f"Користувач {message.from_user.id} відмінив зміну статусу.")
    await state.clear()
    await message.answer(
        text="🖇 Зміна статусу відмінена.",
        reply_markup=create_start_keyboard(True),
    )


@admin_commands_router.message(ChangeUserStatusState.id)
async def set_user_id_handler(message: Message, state: FSMContext):
    user_manager: UserManager = UserManager()
    users = user_manager.load_users()
    target_user_id = message.text.strip()

    if target_user_id.isdigit() and int(target_user_id) in users:
        logger.info(
            f"Користувач {message.from_user.id} вибрав Telegram ID {target_user_id} для зміни статусу.",
        )
        user_status = user_manager.get_user_status(user_id=int(target_user_id))
        await state.update_data(id=int(target_user_id))
        await state.set_state(ChangeUserStatusState.status)
        await message.answer(
            text=f"🚦 Виберіть новий статус для користувача(Current Status:{user_status}):",
            reply_markup=change_status_keyboard,
        )
    else:
        await message.answer(
            "⚠️ Некоректний ID або користувач не знайдений. Введіть правильний Telegram ID.",
        )


@admin_commands_router.message(ChangeUserStatusState.status)
async def handle_new_status_selection(message: Message, state: FSMContext):
    user_manager: UserManager = UserManager()
    new_status = message.text.strip()

    if new_status in ["demo", "unlim", "admin"]:
        data = await state.get_data()
        target_user_id = data.get("id")
        logger.info(
            f"Користувач {message.from_user.id} змінив статус на {new_status} для Telegram ID {target_user_id}.",
        )
        user_manager.update_user_status(
            user_id=target_user_id,
            new_status=new_status,
        )
        await message.answer(
            text=f"✅ Статус користувача з ID {target_user_id} змінено "
            f"на {new_status}.",
            reply_markup=create_start_keyboard(True),
        )
    else:
        await message.answer(
            "⚠️ Некоректний статус. Будь ласка, виберіть із запропонованих варіантів.",
        )
