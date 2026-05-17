import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from database.database import get_session_direct
from dependency import get_user_repo
from models.user import User
import runtime

logger = logging.getLogger(__name__)


class RegistrationForm(StatesGroup):
    waiting_for_token = State()


class ChatBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher(storage=MemoryStorage())
        self._setup_handlers()

    def _setup_handlers(self):
        # Команды
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_help, Command("help"))
        self.dp.message.register(self.cmd_register, Command("register"))
        self.dp.message.register(self.cmd_start_worker, Command("start_worker"))
        self.dp.message.register(self.cmd_stop_worker, Command("stop_worker"))
        self.dp.message.register(self.cmd_status, Command("status"))
        self.dp.message.register(self.cmd_cancel, Command("cancel"), StateFilter("*"))

        # Обработка токена при регистрации
        self.dp.message.register(
            self.handle_token_input,
            RegistrationForm.waiting_for_token,
            F.text
        )

    async def cmd_start(self, message: Message):
        """Приветственное сообщение"""
        await message.answer(
            "👋 Добро пожаловать в FunPay Bot!\n\n"
            "Я помогу автоматизировать общение с клиентами на FunPay.\n\n"
            "Используйте /help для списка команд."
        )

    async def cmd_help(self, message: Message):
        """Список доступных команд"""
        help_text = (
            "📋 <b>Доступные команды:</b>\n\n"
            "/register - Зарегистрироваться и добавить токен FunPay\n"
            "/start_worker - Запустить воркера для обработки сообщений\n"
            "/stop_worker - Остановить воркера\n"
            "/status - Проверить статус воркера\n"
            "/cancel - Отменить текущее действие\n"
            "/help - Показать это сообщение"
        )
        await message.answer(help_text, parse_mode="HTML")

    async def cmd_register(self, message: Message, state: FSMContext):
        """Начало регистрации"""
        tg_id = message.from_user.id

        async with get_session_direct() as session:
            user_repo = get_user_repo(session)
            existing_user = await user_repo.get_by_tg_id(tg_id)

            if existing_user:
                await message.answer(
                    "✅ Вы уже зарегистрированы!\n\n"
                    "Используйте /start_worker для запуска бота."
                )
                return

        await state.set_state(RegistrationForm.waiting_for_token)
        await message.answer(
            "🔑 <b>Регистрация</b>\n\n"
            "Отправьте ваш golden_token от FunPay.\n\n"
            "⚠️ <i>Токен будет сохранён в зашифрованном виде и использован "
            "только для работы с вашим аккаунтом FunPay.</i>\n\n"
            "Для отмены используйте /cancel",
            parse_mode="HTML"
        )

    async def handle_token_input(self, message: Message, state: FSMContext):
        """Обработка введённого токена"""
        token = message.text.strip()
        tg_id = message.from_user.id

        # Удаляем сообщение с токеном для безопасности
        try:
            await message.delete()
        except Exception:
            pass

        # Валидация токена (базовая проверка)
        if len(token) < 20:
            await message.answer(
                "❌ Токен слишком короткий. Пожалуйста, проверьте и отправьте корректный токен."
            )
            return

        try:
            async with get_session_direct() as session:
                user_repo = get_user_repo(session)

                # Создаём нового пользователя
                user = User(
                    tg_id=tg_id,
                    golden_token=token,
                    is_polling=False
                )
                await user_repo.create(user)

            await state.clear()
            await message.answer(
                "✅ <b>Регистрация успешна!</b>\n\n"
                "Теперь вы можете запустить воркера командой /start_worker",
                parse_mode="HTML"
            )
            logger.info(f"User {tg_id} registered successfully")

        except Exception as e:
            logger.exception(f"Error registering user {tg_id}")
            await message.answer(
                "❌ Произошла ошибка при регистрации. Попробуйте позже."
            )

    async def cmd_start_worker(self, message: Message):
        """Запуск воркера"""
        tg_id = message.from_user.id

        try:
            async with get_session_direct() as session:
                user_repo = get_user_repo(session)
                user = await user_repo.get_by_tg_id(tg_id)

                if not user:
                    await message.answer(
                        "❌ Вы не зарегистрированы!\n\n"
                        "Используйте /register для регистрации."
                    )
                    return

                # Проверяем, не запущен ли уже воркер
                if runtime.task_manager.is_running(tg_id):
                    await message.answer("⚠️ Воркер уже запущен!")
                    return

                # Запускаем воркера
                await runtime.task_manager.start_worker(user)

                # Обновляем статус в БД
                user.is_polling = True
                await user_repo.update(user)

            await message.answer(
                "✅ <b>Воркер запущен!</b>\n\n"
                "Бот начал обрабатывать сообщения с FunPay.\n"
                "Вы будете получать уведомления о новых заказах.",
                parse_mode="HTML"
            )
            logger.info(f"Worker started for user {tg_id}")

        except Exception as e:
            logger.exception(f"Error starting worker for user {tg_id}")
            await message.answer(
                "❌ Ошибка при запуске воркера.\n\n"
                "Возможно, токен недействителен. Попробуйте зарегистрироваться заново."
            )

    async def cmd_stop_worker(self, message: Message):
        """Остановка воркера"""
        tg_id = message.from_user.id

        try:
            async with get_session_direct() as session:
                user_repo = get_user_repo(session)
                user = await user_repo.get_by_tg_id(tg_id)

                if not user:
                    await message.answer(
                        "❌ Вы не зарегистрированы!"
                    )
                    return

                # Проверяем, запущен ли воркер
                if not runtime.task_manager.is_running(tg_id):
                    await message.answer("⚠️ Воркер не запущен!")
                    return

                # Останавливаем воркера
                await runtime.task_manager.stop_worker(tg_id)

                # Обновляем статус в БД
                user.is_polling = False
                await user_repo.update(user)

            await message.answer(
                "✅ <b>Воркер остановлен!</b>\n\n"
                "Обработка сообщений приостановлена.",
                parse_mode="HTML"
            )
            logger.info(f"Worker stopped for user {tg_id}")

        except Exception as e:
            logger.exception(f"Error stopping worker for user {tg_id}")
            await message.answer(
                "❌ Ошибка при остановке воркера."
            )

    async def cmd_status(self, message: Message):
        """Проверка статуса воркера"""
        tg_id = message.from_user.id

        try:
            async with get_session_direct() as session:
                user_repo = get_user_repo(session)
                user = await user_repo.get_by_tg_id(tg_id)

                if not user:
                    await message.answer(
                        "❌ Вы не зарегистрированы!\n\n"
                        "Используйте /register для регистрации."
                    )
                    return

                is_running = runtime.task_manager.is_running(tg_id)
                status_emoji = "🟢" if is_running else "🔴"
                status_text = "Запущен" if is_running else "Остановлен"

                await message.answer(
                    f"📊 <b>Статус воркера:</b> {status_emoji} {status_text}\n\n"
                    f"Telegram ID: <code>{tg_id}</code>\n"
                    f"Зарегистрирован: ✅",
                    parse_mode="HTML"
                )

        except Exception as e:
            logger.exception(f"Error checking status for user {tg_id}")
            await message.answer("❌ Ошибка при проверке статуса.")

    async def cmd_cancel(self, message: Message, state: FSMContext):
        """Отмена текущего действия"""
        current_state = await state.get_state()
        if current_state is None:
            await message.answer("Нечего отменять.")
            return

        await state.clear()
        await message.answer(
            "✅ Действие отменено.",
            reply_markup=None
        )

    async def send_order_notification(self, tg_id: int, order_id: str):
        """Отправляет уведомление пользователю о новом заказе"""
        try:
            message = (
                f"🔔 <b>Новый заказ #{order_id}!</b>\n\n"
                f"Пожалуйста, зайдите на FunPay для обработки заказа."
            )
            await self.bot.send_message(chat_id=tg_id, text=message, parse_mode="HTML")
        except Exception as e:
            logger.exception(f"Error sending notification to {tg_id}: {e}")

    async def _run(self):
        logger.info("Telegram bot started...")
        await self.dp.start_polling(self.bot)

    def run(self):
        asyncio.run(self._run())
