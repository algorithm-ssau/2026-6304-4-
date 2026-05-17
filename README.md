# FunPay AI Bot

Автоматизированный бот для FunPay с AI-ответами и Telegram управлением.

## Возможности

- 🤖 **AI-ответы**: Автоматическая генерация ответов клиентам через Ollama
- 📱 **Telegram управление**: Полное управление ботом через Telegram
- 🔔 **Уведомления**: Мгновенные уведомления о новых заказах
- 💾 **История сообщений**: Контекстные ответы на основе истории переписки
- 🔐 **Безопасность**: Защищённое хранение токенов

## Быстрый старт

### 1. Установка зависимостей

```bash
poetry install
```

### 2. Настройка окружения

Создайте файл `.env`:

```env
# AI сервис (Ollama)
AI_URL=http://localhost:11434
MODEL=llama3.2

# Чат бот
BOT_TOKEN=your_bot_token

# База данных (SQLite по умолчанию)
# DATABASE_URL=sqlite+aiosqlite:///./funpay_bot.db

# Окружение
ENVIRONMENT=dev
```

### 3. Применение миграций

```bash
cd src
poetry run alembic upgrade head
```

### 4. Запуск

```bash
poetry run python src/run_bot.py
```

## Использование

### Через Мессенджер

1. Найдите вашего бота в мессенджере
2. Отправьте `/start`
3. Зарегистрируйтесь: `/register`
4. Отправьте ваш FunPay `golden_token`
5. Запустите воркера: `/start_worker`


## Архитектура

```
┌─────────────────┐
│       Bot       │ ← Управление пользователями
└────────┬────────┘
         │
┌────────▼────────┐
│  Task Manager   │ ← Управление воркерами
└────────┬────────┘
         │
┌────────▼────────┐
│ FunPay Worker   │ ← Обработка событий
└─┬──────────────┬┘
  │              │
  ▼              ▼
┌─────────┐  ┌─────────┐
│ AI API  │  │ FunPay  │
└─────────┘  └─────────┘
```

## Документация

- [EVENTS_HANDLING.md](EVENTS_HANDLING.md) - Обработка событий FunPay
- [CLAUDE.md](CLAUDE.md) - Документация для разработчиков

## Технологии

- **FastAPI** - веб-фреймворк
- **aiogram** - Чат bot framework
- **SQLAlchemy** - ORM
- **Ollama** - локальная AI модель
- **FunPayAPI** - интеграция с FunPay
- **SQLite/PostgreSQL** - база данных

## Разработка

### Структура проекта

```
src/
├── main.py                 # FastAPI приложение
├── config.py              # Конфигурация
├── runtime.py             # Singleton объекты
├── gateaway/              # Внешние интеграции
│   ├── ai_api.py          # Ollama API
│   ├── funpay_api.py      # FunPay API
│   └── chat_bot.py        # чат бот
├── workers/               # Воркеры
│   └── funpay_worker.py   # FunPay воркер
├── services/              # Бизнес-логика
│   └── task_manager.py    # Управление воркерами
├── repositories/          # Работа с БД
├── models/                # ORM модели
```

### Команды разработки

```bash
# Создать миграцию
cd src && poetry run alembic revision --autogenerate -m "description"

# Применить миграции
cd src && poetry run alembic upgrade head

# Откатить миграцию
cd src && poetry run alembic downgrade -1
```

## Лицензия

MIT
