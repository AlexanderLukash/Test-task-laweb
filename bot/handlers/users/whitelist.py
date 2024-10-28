import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.requests.utils import extract_domain
from services.users.users import UserManager

from bot.filters.demo import DemoFilter
from bot.keyboards.reply import (
    generate_domain_keyboard,
    return_white_list_menu_keyboard,
    whitelist_keyboard,
)
from bot.utils.states import (
    AddDomainToWhitelistState,
    DeleteDomainFromWhitelistState,
)


whitelist_user_router = Router()
logger = logging.getLogger(__name__)


# Обробник команди для показу меню вайтлиста
@whitelist_user_router.message(DemoFilter(command="🔘 Whitelist"))
async def show_whitelist_menu(message: Message):
    logger.info(f"Користувач {message.from_user.id} відкрив меню вайтлиста")
    await message.answer(
        text="Вітаю у меню вайтлисту! Виберіть дію:",
        reply_markup=whitelist_keyboard,
    )


# Обробник для повернення назад до меню вайтлиста
@whitelist_user_router.message(lambda message: message.text == "Повернутися назад")
async def back_to_whitelist_menu(message: Message, state: FSMContext):
    await state.clear()
    await show_whitelist_menu(message)


# Обробник команди для додавання нового домену до вайтлиста
@whitelist_user_router.message(DemoFilter(command="Додати домен"))
async def request_domain(message: Message, state: FSMContext):
    logger.info(f"Користувач {message.from_user.id} почав додавати домен до вайтлиста")
    user_manager = UserManager()

    # Завантажуємо дані користувача
    user_data = user_manager.get_user_info(message.from_user.id)

    if not user_data:
        await message.answer("⚠️ Ви не зареєстровані. Напишіть боту /start")
        return

    # Перевірка ліміту на домени
    user_domains = user_data.get("whitelist", [])
    if user_data.get("status") != "admin" and len(user_domains) >= 3:
        await message.answer("❌ Ви не можете додати більше 3-х доменів.")
        return
    await state.set_state(AddDomainToWhitelistState.domain)
    await message.answer(
        text="📩 Відправте посилання на сайт, домен якого ви хочете додати.",
        reply_markup=return_white_list_menu_keyboard,
    )


# Обробник для додавання домену після введення користувачем
@whitelist_user_router.message(AddDomainToWhitelistState.domain)
async def add_domain(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_domain = message.text
    user_manager = UserManager()

    domain = extract_domain(user_domain)
    if domain:
        if domain not in user_manager.get_user_whitelist(user_id):
            success = user_manager.add_to_whitelist(user_id, domain)
            if success:
                logger.info(f"Користувач {user_id} додав домен {domain} до вайтлиста")
                await message.answer(f"✅ Домен {domain} успішно додано до вайтлиста.")
            else:
                await message.answer(
                    "❌ Ліміт доменів досягнуто для цього користувача.",
                )
        else:
            await message.answer("❌ Цей домен вже додано до вайтлиста.")
    else:
        await message.answer("❌ Введіть коректний URL.")

    await state.clear()
    await show_whitelist_menu(message)


# Обробник команди для перегляду списку доменів у вайтлисті
@whitelist_user_router.message(DemoFilter(command="Список доменів"))
async def list_domains(message: Message, state: FSMContext):
    logger.info(f"Користувач {message.from_user.id} відкрив список доменів")
    user_id = message.from_user.id
    user_manager = UserManager()
    user_domains = user_manager.get_user_whitelist(user_id)

    if not user_domains:
        await message.answer("📋 Ваш вайтлист порожній.")
    else:
        domain_keyboard = generate_domain_keyboard(user_domains)
        await state.set_state(DeleteDomainFromWhitelistState.domain)
        await message.answer(
            "Виберіть домен, який хочете видалити:",
            reply_markup=domain_keyboard,
        )


# Обробник для видалення домену з вайтлиста
@whitelist_user_router.message(DeleteDomainFromWhitelistState.domain)
async def delete_domain(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_manager = UserManager()
    domain_to_remove = message.text

    if user_manager.remove_from_whitelist(user_id, domain_to_remove):
        logger.info(
            f"Користувач {user_id} видалив домен {domain_to_remove} з вайтлиста",
        )
        await message.answer(f"✅ Домен {domain_to_remove} видалено з вайтлиста.")
    else:
        await message.answer("❌ Домен не знайдено у вашому вайтлисті.")

    await state.clear()
    await list_domains(message, state)
