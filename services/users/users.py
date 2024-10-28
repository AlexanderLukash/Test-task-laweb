import json
import logging
import os
from dataclasses import (
    asdict,
    dataclass,
    field,
)
from typing import Dict

from services.users.entities.users import UserEntity
from settings.config import Config


config: Config = Config()
logger = logging.getLogger(__name__)

USERS_FILE = config.USERS_FILE_NAME


# Менеджер користувачів для управління завантаженням, збереженням та реєстрацією даних користувачів
@dataclass
class UserManager:
    users_file: str = USERS_FILE
    users: Dict[int, UserEntity] = field(default_factory=dict)
    last_modified_time: float = field(default_factory=lambda: 0)

    def load_users(self) -> dict:
        """Завантажує дані користувача з вказаного JSON-файлу."""
        try:
            current_modified_time = os.path.getmtime(
                self.users_file,
            )  # Отримуємо час модифікації файлу
            if (
                current_modified_time != self.last_modified_time
            ):  # Перевіряємо, чи файл змінився
                with open(self.users_file) as file:
                    data = json.load(file)
                    self.users = {
                        int(user_id): UserEntity(**user_data)
                        for user_id, user_data in data.items()
                    }
                self.last_modified_time = (
                    current_modified_time  # Оновлюємо час модифікації
                )
            return self.users
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {}
            return self.users

    def save_users(self) -> None:
        """Зберігає поточні дані користувача у вказаний JSON-файл."""
        with open(self.users_file, "w") as file:
            json.dump(
                {user_id: asdict(user) for user_id, user in self.users.items()},
                file,
                indent=4,
            )

    def register_user(self, user_id: int) -> None:
        """Реєструє нового користувача, якщо він ще не зареєстрований."""
        self.load_users()
        if user_id not in self.users:
            self.users[user_id] = UserEntity(id=user_id)
            self.save_users()

    def get_user_status(self, user_id: int) -> str | None:
        """Повертає статус користувача за його ID."""
        self.load_users()
        user_data = self.users.get(user_id)
        return user_data.status if user_data else None

    def update_user_status(self, user_id: int, new_status: str) -> None:
        """Оновлює статус користувача за його ID."""
        self.load_users()
        if user_id in self.users:
            self.users[user_id].status = new_status
            self.save_users()

    def get_user_info(self, user_id: int) -> dict | None:
        """Повертає інформацію про користувача у вигляді словника."""
        self.load_users()
        user = self.users.get(user_id)
        return asdict(user) if user else None

    def add_to_whitelist(self, user_id: int, domain: str) -> bool:
        """Додає домен до whitelist користувача, якщо не перевищено ліміт."""
        self.load_users()
        user = self.users.get(user_id)

        if not user:
            self.register_user(user_id)
            user = self.users[user_id]

        if user.status != "admin" and len(user.whitelist) >= 3:
            return False  # Ліміт досягнуто для не-адміністраторів

        user.whitelist.append(domain)
        self.save_users()
        return True

    def get_user_whitelist(self, user_id: int) -> list[str]:
        """Повертає whitelist доменів користувача."""
        self.load_users()
        user = self.users.get(user_id)
        return user.whitelist if user else []

    def remove_from_whitelist(self, user_id: int, domain: str) -> bool:
        """Видаляє домен з whitelist користувача, якщо він існує."""
        self.load_users()
        user = self.users.get(user_id)

        if user and domain in user.whitelist:
            user.whitelist.remove(domain)
            self.save_users()
            return True
        return False

    def is_demo_limit_reached(self, user_id: int) -> bool:
        """Перевіряє, чи досяг користувач ліміту заявок у статусі 'demo'."""
        self.load_users()
        user = self.users.get(user_id)
        return user.applications_sent >= 50 if user and user.status == "demo" else False

    def increment_applications_sent(self, user_id: int) -> None:
        """Збільшує кількість надісланих заявок користувача."""
        self.load_users()
        user = self.users.get(user_id)
        if user:
            user.applications_sent += 1
            self.save_users()

    def reset_applications_sent(self, user_id: int) -> None:
        """Скидає кількість надісланих заявок користувача."""
        self.load_users()
        user = self.users.get(user_id)
        if user:
            user.applications_sent = 0
            self.save_users()

    def add_active_session(self, user_id: int, url: str) -> bool:
        """Додає URL до активних сесій користувача."""
        self.load_users()
        user = self.users.get(user_id)
        if user and url not in user.active_sessions:
            user.active_sessions.append(url)
            self.save_users()
            return True
        return False

    def remove_active_session(self, user_id: int, url: str) -> bool:
        """Видаляє URL з активних сесій користувача."""
        self.load_users()
        user = self.users.get(user_id)
        if user and url in user.active_sessions:
            user.active_sessions.remove(url)
            self.save_users()
            return True
        return False

    def clear_active_sessions(self, user_id: int) -> None:
        """Очищає всі активні сесії користувача."""
        self.load_users()
        user = self.users.get(user_id)
        if user:
            user.active_sessions.clear()
            self.save_users()

    def is_session_active(self, user_id: int, url: str) -> bool:
        """Перевіряє, чи є певна URL сесія активною для користувача."""
        self.load_users()
        user = self.users.get(user_id)
        return url in user.active_sessions if user else False

    def get_active_session_count(self, user_id: int) -> int:
        """Повертає кількість активних сесій для користувача."""
        self.load_users()
        user = self.users.get(user_id)
        return len(user.active_sessions) if user else 0
