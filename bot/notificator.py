import logging


logger = logging.getLogger(__name__)


# Відправляє повідомлення користувачу про завершення відправки заявок
async def notify_user_completion(
    user_id: int,
    successful_requests: int,
    url: str,
) -> None:
    message_text = f"✅ Відправка заявок на сайт: {url} завершена. Всього успішно відправлено заявок: {successful_requests}!"

    try:
        from bot.main import bot

        await bot.send_message(chat_id=user_id, text=message_text)
        logger.info(
            f"Повідомлення надіслано користувачу {user_id} про завершення заявок.",
        )
    except Exception as e:
        logger.error(f"Помилка при відправці повідомлення користувачу {user_id}: {e}")
