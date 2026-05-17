# Быстрый старт

## 1. Установка

```bash
poetry install
```

## 2. Настройка .env

```env
AI_URL=http://localhost:11434
MODEL=llama3.2
BOT_TOKEN=your_telegram_bot_token_here
ENVIRONMENT=dev
```

## 3. Миграции

```bash
cd src
poetry run alembic upgrade head
cd ..
```

## 4. Запуск

**Терминал 1 - Telegram бот:**
```bash
poetry run python src/run_telegram_bot.py
```

**Терминал 2 - FastAPI сервер:**
```bash
cd src
poetry run uvicorn app:app --reload
```

## 5. Использование

1. Найдите бота в Telegram
2. `/start` - начало работы
3. `/register` - регистрация и добавление FunPay токена
4. `/start_worker` - запуск автоматической обработки
5. `/status` - проверка статуса

## Готово!

Бот начнёт автоматически отвечать на сообщения клиентов через AI и присылать уведомления о новых заказах.

## Проверка

Сервер доступен по адресу: http://127.0.0.1:8000
API документация: http://127.0.0.1:8000/docs
