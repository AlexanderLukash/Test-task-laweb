from aiogram.filters import BaseFilter
from aiogram.types import Message

from services.users.users import UserManager


class AdminFilter(BaseFilter):
    is_admin: bool = True

    async def __call__(self, obj: Message) -> bool:
        user_manager = UserManager()  # Ініціалізуємо менеджер користувачів
        user_status = user_manager.get_user_status(
            obj.from_user.id,
        )  # Отримуємо статус користувача
        return user_status == "admin"
