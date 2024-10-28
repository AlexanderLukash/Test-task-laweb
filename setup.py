import asyncio

from settings.logger import setup_logging

from bot.main import start_bot


# Запуск бота при запуску скрипта
if __name__ == "__main__":
    setup_logging()
    asyncio.run(start_bot())
