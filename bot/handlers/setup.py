import logging

from aiogram import Dispatcher

from bot.handlers.admins.admin_commands import admin_commands_router
from bot.handlers.admins.start import start_admin_router
from bot.handlers.users.applications import applications_user_router
from bot.handlers.users.other import other_user_router
from bot.handlers.users.profile import profile_users_router
from bot.handlers.users.start import start_user_router
from bot.handlers.users.whitelist import whitelist_user_router


logger = logging.getLogger(__name__)


# Функція для реєстрації всіх роутерів в диспетчері
def register_routers(dp: Dispatcher):
    dp.include_router(start_admin_router)
    dp.include_router(admin_commands_router)
    dp.include_router(start_user_router)
    dp.include_router(profile_users_router)
    dp.include_router(other_user_router)
    dp.include_router(applications_user_router)
    dp.include_router(whitelist_user_router)
    logger.info("Маршрутизатор команд успішно зареєстровано")
