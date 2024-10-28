import logging

from aiogram import (
    Bot,
    Dispatcher,
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from settings.config import Config

from bot.handlers.setup import register_routers


config: Config = Config()

bot = Bot(
    token=config.token,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)
dp = Dispatcher()
logger = logging.getLogger(__name__)


# Функція запуску бота
async def start_bot():
    register_routers(dp)

    logger.info("Бота запущено!")
    # Видалення будь-якого існуючого веб-хука
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
