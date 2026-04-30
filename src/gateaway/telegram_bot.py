import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

class Form(StatesGroup):
    waiting_string = State()

async def start(message: Message):
    print(f"User ID: {message.from_user.id}")
    await message.answer("Привет! Введи /input чтобы начать")

async def input_command(message: Message, state: FSMContext):
    await state.set_state(Form.waiting_string)
    await message.answer("Введи строку:")

async def handle_string(message: Message, state: FSMContext):
    text = message.text
    if text.lstrip('-').replace('.', '', 1).isdigit():
        await message.answer("Ошибка: введи строку, а не число. Попробуй снова:")
        return
    await state.clear()
    await message.answer(f"Получено: {text}")

async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.")

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
