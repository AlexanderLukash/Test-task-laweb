from aiogram.filters import BaseFilter
from aiogram.types import Message

from services.users.users import UserManager


class DemoFilter(BaseFilter):
    is_demo: bool = False
    command: str = None

    def __init__(self, command: str):
        self.command = command

    async def __call__(self, obj: Message) -> bool:
        user_manager = UserManager()  # Ініціалізуємо менеджер користувачів
        user_status = user_manager.get_user_status(
            obj.from_user.id,
        )  # Отримуємо статус користувача

        if self.command and obj.text != self.command:
            return False

        if user_status == "demo":
            await obj.answer("❌ Ця функція доступна тільки у платній версії боту.")
            return False  # Забороняємо доступ до хендлера
        return True
