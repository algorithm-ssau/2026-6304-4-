from gateaway.telegram_bot import ChatBot
from services.task_manager import TaskManager


task_manager = TaskManager()

# Telegram bot инициализируется отдельно в run_telegram_bot.py
chat_bot: ChatBot | None = None