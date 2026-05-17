"""
Запуск Telegram бота
"""
import asyncio
import logging

from config import get_config
from gateaway.telegram_bot import ChatBot
import runtime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    config = get_config()

    if not config.telegram.bot_token:
        logger.error("Chat bot token not configured in .env file (BOT_TOKEN)")
        return

    # Инициализируем telegram_bot в runtime
    chat_bot = ChatBot(config.telegram.bot_token)
    runtime.chat_bot = chat_bot

    logger.info("Starting Chat bot...")
    await chat_bot._run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Chat bot stopped by user")
