import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message


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
