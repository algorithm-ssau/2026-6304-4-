# Обработка событий FunPay

## Описание

Реализована обработка двух типов событий от FunPay:

1. **Новые сообщения** - автоматически отправляются в AI (Ollama) для генерации ответа
2. **Новые заказы** - отправляется уведомление в Telegram пользователю

## Настройка

### 1. Переменные окружения (.env)

```env
# База данных (SQLite по умолчанию для разработки)
# DATABASE_URL не указан = используется sqlite+aiosqlite:///./funpay_bot.db
# Для PostgreSQL раскомментируйте:
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/funpay_ai_agent

# AI сервис (Ollama)
AI_URL=http://localhost:11434
MODEL=llama3.2

# Telegram бот
BOT_TOKEN=your_telegram_bot_token

# Окружение
ENVIRONMENT=dev
```

### 2. Миграция базы данных

```bash
cd src
poetry run alembic upgrade head
```

База данных SQLite будет создана автоматически в файле `funpay_bot.db` в корне проекта.

## Как работает

### Обработка новых сообщений

1. FunPay worker получает событие `NEW_MESSAGE`
2. Текст сообщения отправляется в Ollama API
3. История последних 20 сообщений загружается из БД для контекста
4. AI генерирует ответ
5. Ответ отправляется обратно в чат FunPay
6. Сообщения сохраняются в БД

### Обработка новых заказов

1. FunPay worker получает событие `NEW_ORDER`
2. Отправляется уведомление в Telegram пользователю с ID заказа
3. Пользователь получает сообщение: "🔔 Новый заказ #12345! Пожалуйста, зайдите на FunPay для обработки заказа."

## Структура кода

- `src/workers/funpay_worker.py` - обработчики событий `_handle_new_message()` и `_handle_new_order()`
- `src/gateaway/ai_api.py` - интеграция с Ollama API
- `src/gateaway/telegram_bot.py` - отправка уведомлений в Telegram
- `src/repositories/messages.py` - работа с историей сообщений
- `src/runtime.py` - инициализация singleton объектов (task_manager, telegram_bot)

## Запуск

```bash
# Запустить FastAPI сервер
poetry run uvicorn src.app:app --reload

# Запустить worker для пользователя
curl -X POST "http://localhost:8000/ai/start?token=YOUR_FUNPAY_TOKEN"

# Остановить все workers
curl -X DELETE "http://localhost:8000/ai/stop?tg_id=123456"
```

## Примечания

- История сообщений ограничена 20 последними сообщениями на пользователя
- Старые сообщения автоматически удаляются при превышении лимита
- Telegram бот инициализируется только если указан BOT_TOKEN
- AI ответы генерируются асинхронно, не блокируя другие события
- SQLite используется по умолчанию для разработки (не требует установки PostgreSQL)
- Для продакшена рекомендуется использовать PostgreSQL
