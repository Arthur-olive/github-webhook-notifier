import logging

logger = logging.getLogger(__name__)

async def send_telegram_message(text: str):

    logger.info("[WEBHOOK NOTIFIER] %s", text)
