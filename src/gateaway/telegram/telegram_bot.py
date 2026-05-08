import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

class Form(StatesGroup):
    waiting_string = State()

class TelegramBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher(storage=MemoryStorage())
        self._setup_handlers()

    def _setup_handlers(self):
        self.dp.message.register(start, Command("start"))
        self.dp.message.register(input_command, Command("input"))
        self.dp.message.register(cancel, Command("cancel"))
        self.dp.message.register(handle_string, Form.waiting_string, F.text)

    async def _run(self):
        print("Бот запущен...")
        await self.dp.start_polling(self.bot)

    def run(self):
        asyncio.run(self._run())

if __name__ == "__main__":
    bot = TelegramBot("YOUR_TOKEN_HERE")
    bot.run()