import asyncio
import logging
import random
import time
from typing import (
    Optional,
    Tuple,
)
from urllib.parse import (
    urlsplit,
    urlunsplit,
)

import aiohttp
from aiohttp import (
    ClientSession,
    TCPConnector,
)
from bs4 import BeautifulSoup
from services.requests.exceptions.requests import (
    FormNotFoundException,
    ProxyErrorException,
    SiteUnavailableException,
)
from services.requests.proxy_manager import ProxyManager
from services.requests.utils import (
    generate_name,
    generate_phone_number,
)
from services.users.users import UserManager

from bot.notificator import notify_user_completion


logger = logging.getLogger(__name__)


class RequestManager:
    proxy_manager: ProxyManager = ProxyManager()
    user_manager: UserManager = UserManager()

    # Додаємо лічильник для успішних заявок
    successful_requests = {}  # Словник для зберігання кількості заявок { (user_id, url): count }

    def increment_successful_requests(self, user_id: int, url: str):
        """Збільшує лічильник успішних заявок для певного користувача і URL."""
        if (user_id, url) not in self.successful_requests:
            self.successful_requests[(user_id, url)] = 0
        self.successful_requests[(user_id, url)] += 1

    def get_successful_requests(self, user_id: int, url: str) -> int:
        """Повертає кількість успішних заявок для певного користувача і URL."""
        return self.successful_requests.get((user_id, url), 0)

    def reset_successful_requests(self, user_id: int, url: str):
        """Скидає лічильник успішних заявок для певного користувача і URL."""
        self.successful_requests.pop((user_id, url), None)

    async def send_request(
        self,
        session: ClientSession,
        proxy_url: Optional[str],
        url: str,
        headers: dict,
    ) -> Tuple[
        Optional[str],
        Optional[dict],
    ]:
        """Надішліть один GET-запит і форму розбору для наступного POST-запиту."""
        logger.info(f"Відправлення GET-запиту на: {url}")

        try:
            async with session.get(url, proxy=proxy_url, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"Failed to GET: {url} with status: {response.status}")
                    raise SiteUnavailableException()

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                form = soup.find("form")

                if not form:
                    raise FormNotFoundException()

                action = form.get("action")
                if action:
                    action = self.form_action_url(url, action)
                data = self.extract_form_data(form)

                return action, data
        except aiohttp.ClientProxyConnectionError:
            logger.error("Помилка підключення проксі-сервера.")
            raise ProxyErrorException()
        except aiohttp.ClientError as e:
            logger.error(f"Неочікувана помилка: {e}")
            raise SiteUnavailableException()

    @staticmethod
    def form_action_url(base_url: str, action: str) -> str:
        """Formulates the URL for form action."""
        if not action.startswith("http"):
            split_url = urlsplit(base_url)
            base_url_without_query = urlunsplit(
                (
                    split_url.scheme,
                    split_url.netloc,
                    split_url.path.rstrip("/") + "/",
                    "",
                    "",
                ),
            )
            action = f"{base_url_without_query}{action.lstrip('/')}"
        logger.info(f"Сформована URL-адреса дії: {action}")
        return action

    @staticmethod
    def extract_form_data(form) -> dict:
        """Витягує дані з форми для відправки POST"""
        data = {}
        inputs = form.find_all("input")
        for input_tag in inputs:
            input_name = input_tag.get("name")
            input_type = input_tag.get("type")

            if input_type == "name" or input_name == "name":
                data[input_name] = generate_name()
            elif input_type == "tel" or input_name == "phone" or input_name == "tel":
                data[input_name] = generate_phone_number()
            elif input_type == "checkbox":
                data[input_name] = "on"

        selects = form.find_all("select")
        for select in selects:
            select_name = select.get("name")
            options = select.find_all("option")
            valid_options = [option for option in options if option.get("value")]
            if valid_options:
                selected_option = random.choice(valid_options).get("value")
                data[select_name] = selected_option

        logger.info(f"Дані, які потрібно надіслати: {data}")
        return data

    async def send_form(
        self,
        session: ClientSession,
        action: str,
        data: dict,
        proxy_url: Optional[str],
    ) -> Optional[str]:
        """Спроби відправити форму з повторними спробами"""
        for attempt in range(3):
            async with session.post(
                action,
                data=data,
                proxy=proxy_url,
            ) as post_response:
                if post_response.status == 200:
                    logger.info(f"Запит до {action} відправлено успішно.")
                    return None  # Успішно відправлено
                else:
                    logger.error(f"Помилка при відправці: {post_response.status}")
                    if attempt < 2:
                        await asyncio.sleep(10)  # Затримка перед повторною спробою
        return "Не вдалося надіслати форму."

    async def request_loop(
        self,
        user_id: int,
        url: str,
        frequency: str,
        duration: Optional[int] = None,
    ) -> None:
        """Основний цикл для керування відправкою запитів"""
        delay_mapping = {
            "Без затримки 🚀": 0,
            "1 заявка в 10 секунд ⏳": 10,
            "1 заявка в 10 хвилин ⌛": 600,
            "1 заявка в 60 хвилин ⌛": 3600,
        }
        delay = delay_mapping.get(frequency, 0)
        user_info = self.user_manager.get_user_info(user_id)

        requests_to_send = (
            50 - user_info["applications_sent"]
            if user_info.get("status") == "demo"
            else float("inf")
        )
        end_time = time.time() + duration if duration else None

        while requests_to_send > 0:
            if end_time and time.time() >= end_time:
                break

            proxy_url = self.proxy_manager.get_proxy()
            logger.info(
                f"Використовую проксі: {proxy_url}"
                if proxy_url
                else "Відправлення запиту без проксі.",
            )

            async with ClientSession(connector=TCPConnector(ssl=False)) as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
                }

                try:
                    action, data = await self.send_request(
                        session,
                        proxy_url,
                        url,
                        headers,
                    )
                    if not action or data is None:
                        break  # Продовжити неможливо без коректної форми

                    error_message = await self.send_form(
                        session,
                        action,
                        data,
                        proxy_url,
                    )
                    if error_message:
                        logger.error("Помилка заповнення форми, зупинка запитів.")
                        break

                    # Оновлення даних після успішної заявки
                    self.user_manager.increment_applications_sent(user_id)
                    self.increment_successful_requests(
                        user_id,
                        url,
                    )  # Збільшення лічильника успішних заявок

                except FormNotFoundException:
                    logger.error("Форма не знайдена на сторінці. Зупинка запитів.")
                    break
                except SiteUnavailableException:
                    logger.error("Сайт недоступний, повторна спроба після затримки.")
                    await asyncio.sleep(5)
                    continue
                except ProxyErrorException:
                    logger.error("Помилка проксі, спробуйте з новим проксі.")
                    continue

            # Зменшуємо ліміт запитів, якщо користувач на демо-аккаунті
            if user_info.get("status") == "demo":
                requests_to_send -= 1

            await asyncio.sleep(delay)

        # Завершення активної сесії
        self.user_manager.remove_active_session(user_id, url)
        self.user_manager.save_users()

        # Відправляємо повідомлення користувачу про завершення циклу
        successful_requests = self.get_successful_requests(user_id, url)
        await notify_user_completion(user_id, successful_requests, url)

        # Очищаємо лічильник для цього завдання
        self.reset_successful_requests(user_id, url)

        logger.info(
            f"Завершено цикл запиту для user_id: {user_id}. Всього відправлено запитів: {user_info['applications_sent']}.",
        )
