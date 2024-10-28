import asyncio
import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from services.requests.request import RequestManager
from services.requests.utils import (
    extract_domain,
    is_valid_url,
)
from services.users.users import UserManager

from bot.keyboards.reply import (
    applications_main_menu_keyboard,
    applications_start_cancel_keyboard,
    create_duration_keyboard,
    frequency_keyboard,
)
from bot.notificator import notify_user_completion
from bot.utils.states import StartApplicationState


applications_user_router = Router()
logger = logging.getLogger(__name__)
request_manager = RequestManager()
user_manager = UserManager()  # Ініціалізація UserManager

# Словник для зберігання активних завдань
active_tasks = {}


@applications_user_router.message(lambda message: message.text == "🚀 Відправка заявок")
async def applications_menu_handler(message: Message):
    logger.info(f"User {message.from_user.id} відкрив меню заявок")
    await message.answer(
        text="Виберіть дію з заявками.",
        reply_markup=applications_main_menu_keyboard,
    )


@applications_user_router.message(
    lambda message: message.text == "Скасувати відправку ❌"
    or message.text == "В меню заявок",
)
async def back_to_applications_menu(message: Message, state: FSMContext):
    logger.info(f"User {message.from_user.id} повернувся до меню заявок")
    await state.clear()
    await applications_menu_handler(message)


@applications_user_router.message(
    lambda message: message.text == "❌ Зупинити відправку",
)
async def stop_application_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"User {user_id} обрав 'Зупинити відправку'")
    data = await state.get_data()
    url = data.get("url")

    # Зупиняємо завдання, якщо воно активне
    task = active_tasks.get((user_id, url))
    if task and not task.done():
        task.cancel()  # Скасовуємо завдання
        successful_requests = request_manager.get_successful_requests(user_id, url)
        await notify_user_completion(user_id, successful_requests, url)
        await message.answer("⛔️ Відправка заявок зупинена.")
    else:
        await message.answer("❌ Немає активного завдання для зупинки.")

    # Видаляємо сесію і завдання з активних списків
    user_manager.remove_active_session(user_id, url)
    active_tasks.pop((user_id, url), None)
    await state.clear()
    await applications_menu_handler(message)


@applications_user_router.message(
    lambda message: message.text == "Запустити відправку 🚀",
)
async def initiate_request(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"User {user_id} обрав 'Запустити відправку заявок'")

    # Перевірка статусу і ліміту
    user_data = user_manager.get_user_info(user_id)
    applications_sent = user_data.get("applications_sent")

    if user_data.get("status") == "demo":
        if user_manager.get_active_session_count(user_id) >= 1:
            await message.answer(
                "❌ Для демо статусу доступна тільки 1 заявка одночасно.",
            )
            return
        if user_manager.is_demo_limit_reached(user_id):
            await message.answer(
                "❌ Ви вже досягли ліміту в 50 заявок. Для отримання повного доступу зверніться до адміністратора.",
            )
            return

    if (
        user_data.get("status") == "unlim"
        and user_manager.get_active_session_count(user_id) >= 3
    ):
        await message.answer("❌ Для демо статусу доступна тільки 3 заявки одночасно.")
        return

    # Запит URL
    if user_data.get("status") == "demo":
        requests_to_send = 50 - applications_sent
        await message.answer(
            text=f"🌐 Ви можете надіслати ще до {requests_to_send} заявок. Введіть посилання на сайт:",
            reply_markup=applications_start_cancel_keyboard,
        )
    else:
        await message.answer(
            text="🌐 Введіть посилання на сайт:",
            reply_markup=applications_start_cancel_keyboard,
        )
    await state.set_state(StartApplicationState.url)


@applications_user_router.message(StartApplicationState.url)
async def handle_url(message: Message, state: FSMContext):
    url = message.text
    domain = extract_domain(url)
    logger.info(f"User {message.from_user.id} ввів URL: {url}")

    # Перевірка домену на існування у вайтлісті інших користувачів
    if any(domain in data.whitelist for data in user_manager.load_users().values()):
        await message.answer(
            f"❌ Домен '{domain}' вже існує у вайтлісті іншого користувача. Будь ласка, введіть інший домен.",
        )
        return

    if is_valid_url(url):
        await state.update_data(url=url)
        await state.set_state(StartApplicationState.delay)
        await message.answer(
            "🕰 Як швидко будуть відправлятися заявки?",
            reply_markup=frequency_keyboard,
        )
    else:
        await message.answer("⚠️ Будь ласка, введіть коректне посилання на сайт")


@applications_user_router.message(StartApplicationState.delay)
async def handle_frequency_and_duration(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = user_manager.get_user_info(user_id)
    logger.info(f"User {user_id} обрав затримку для відправки заявок: {message.text}")

    # Установка затримки
    if message.text in [
        "Без затримки 🚀",
        "1 заявка в 10 секунд ⏳",
        "1 заявка в 10 хвилин ⌛",
        "1 заявка в 60 хвилин ⌛",
    ]:
        delay = message.text
        await state.update_data(delay=delay)

        if user_data.get("status") == "demo":
            await message.answer(
                "💫 Частота обрана. Вибір тривалості відправки заявок у демо статусі недоступний.",
            )
            data = await state.get_data()
            website_url = data.get("url")
            await state.clear()
            if user_manager.add_active_session(user_id, website_url):
                await message.answer(
                    f"🚀 Відправка заявок на сайт: {website_url} розпочата.",
                    reply_markup=applications_main_menu_keyboard,
                )

                # Створення завдання для циклу запитів
                task = asyncio.create_task(
                    request_manager.request_loop(
                        user_id,
                        website_url,
                        delay,
                        duration=None,
                    ),
                )
                active_tasks[(user_id, website_url)] = task
                return
            else:
                await message.answer(
                    "❌ Ви вже маєте активну сесію для цього сайту.",
                    reply_markup=applications_main_menu_keyboard,
                )
                return

        await state.set_state(StartApplicationState.duration)
        await message.answer(
            "⏳ Як довго будуть відправлятися заявки?",
            reply_markup=create_duration_keyboard(
                True if user_manager.get_user_status(user_id) == "admin" else False,
            ),
        )


@applications_user_router.message(StartApplicationState.duration)
async def handle_duration(message: Message, state: FSMContext):
    user_id = message.from_user.id
    duration_mapping = {
        "1 хвилина ⏳": 60,
        "15 хвилин ⏳": 15 * 60,
        "30 хвилин ⏳": 30 * 60,
        "1 година ⏳": 60 * 60,
        "3 години ⏳": 3 * 60 * 60,
        "Необмежено ⏳": None,
    }

    duration = duration_mapping.get(message.text)
    if duration is None:
        await message.answer(
            "❌ Невірний вибір тривалості. Будь ласка, виберіть тривалість з меню.",
        )
        return

    # Старт циклу запитів з заданою тривалістю
    data = await state.get_data()
    delay = data.get("delay")
    website_url = data.get("url")
    await state.clear()
    if user_manager.add_active_session(user_id, website_url):
        await message.answer(
            f"🚀 Відправка заявок на сайт: {website_url} розпочата.",
            reply_markup=applications_main_menu_keyboard,
        )

        # Створення і збереження завдання
        task = asyncio.create_task(
            request_manager.request_loop(user_id, website_url, delay, duration),
        )
        active_tasks[(user_id, website_url)] = task
        return
    else:
        await message.answer(
            "❌ Ви вже маєте активну сесію для цього сайту.",
            reply_markup=applications_main_menu_keyboard,
        )
        return


@applications_user_router.message(lambda message: message.text == "Активні сесії 🕜")
async def show_active_sessions(message: Message):
    user_id = message.from_user.id
    logger.info(f"User {user_id} переглядає активні сесії")
    user_active_sessions = [
        (user, url) for (user, url) in active_tasks.keys() if user == user_id
    ]

    if user_active_sessions:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=url, callback_data=f"stop_session:{url}")]
                for _, url in user_active_sessions
            ],
        )
        await message.answer("Ваші активні сесії:", reply_markup=keyboard)
    else:
        await message.answer("У вас немає активних сесій.")


@applications_user_router.callback_query(
    lambda callback: callback.data.startswith("stop_session:"),
)
async def stop_session_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    url = callback_query.data.split("stop_session:")[1]
    logger.info(f"User {user_id} зупиняє сесію для URL: {url}")

    task_key = (user_id, url)
    task = active_tasks.get(task_key)

    if task and not task.done():
        successful_requests = request_manager.get_successful_requests(user_id, url)
        await notify_user_completion(user_id, successful_requests, url)
        task.cancel()
        active_tasks.pop(task_key, None)
        user_manager.remove_active_session(user_id, url)
        await callback_query.message.answer(
            f"⛔️ Сесія для {url} була успішно зупинена.",
            reply_markup=applications_main_menu_keyboard,
        )
    else:
        await callback_query.message.answer("❌ Сесія неактивна або вже була зупинена.")

    await callback_query.message.delete()
