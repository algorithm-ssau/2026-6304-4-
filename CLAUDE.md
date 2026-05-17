# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MarketplaceBot is a FastAPI-based bot that integrates FunPay marketplace with AI chat capabilities and Telegram. It manages long-running worker tasks that poll FunPay for new messages and respond using AI.

## Architecture

### Core Components

**Gateway Layer** (`src/gateaway/`):
- `funpay_api.py`: FunPay API wrapper using the `FunPayAPI` library
- `ai_api.py`: AI service abstraction (currently incomplete, designed for Ollama)
- `telegram_bot.py`: Telegram bot using aiogram for user interaction

**Worker System** (`src/workers/`, `src/services/task_manager.py`):
- `FunpayWorker`: Runs FunPay polling in a separate thread, bridges sync FunPayAPI with async FastAPI
- `TaskManager`: Manages worker lifecycle (start/stop/restart) per user account, uses asyncio locks for thread safety
- Workers are keyed by `tg_id` (Telegram user ID) and run independently per user

**Threading Model**:
- FunPay's `Runner.listen()` is synchronous and blocking
- Each `FunpayWorker` spawns a daemon thread running `_polling_thread()`
- Events from the sync thread are pushed to an async queue via `asyncio.run_coroutine_threadsafe()`
- Main async loop processes events from the queue

**Dependency Injection** (`src/dependency.py`):
- FastAPI dependencies for repositories and services
- `runtime.py` holds the singleton `task_manager` instance

**Database**:
- SQLAlchemy async with PostgreSQL (asyncpg driver) or SQLite (aiosqlite driver)
- PostgreSQL-specific connection parameters (server_settings, command_timeout) are applied conditionally
- Soft-delete mixin with `deleted_at`/`deleted_by` fields
- Session management via `get_session()` (FastAPI dependency) and `get_session_direct()` (context manager for workers)
- Connection pooling configured differently for production vs non-production

**Routes** (`src/routes/`):
- Auto-discovery: `__init__.py` imports all `*.py` files with a `router` attribute
- `/ai/start`: Starts a FunPay worker for a user (requires `token` and creates mock User)
- `/ai/stop`: Stops all workers (currently stops all, not per-user)
- `/auth/*`: Placeholder endpoints (commented out)

## Development Commands

### Setup
```bash
poetry install
```

### Database Migrations
Alembic is configured in `alembic.ini` (project root) with migrations in `src/alembic/versions/`.

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Running the Application
```bash
# Development server
poetry run uvicorn src.app:app --reload

# Production
poetry run uvicorn src.app:app --host 0.0.0.0 --port 8000
```

### Environment Variables
Required in `.env` at project root:
- `DATABASE_URL`: Database connection string
  - SQLite (dev): `sqlite+aiosqlite:///./funpay_bot.db`
  - PostgreSQL (prod): `postgresql+asyncpg://user:pass@host:port/dbname`
- `ENVIRONMENT`: `production` or other (affects DB pool size)
- `AI_URL`: AI service endpoint
- `MODEL`: AI model name
- `BOT_TOKEN`: Telegram bot token
- `SSL_CERT_PATH`: Optional SSL certificate path for DB connection (PostgreSQL only)

## Key Patterns

**Worker Lifecycle**:
1. User calls `/ai/start` with FunPay `golden_token`
2. `TaskManager.start_worker()` creates `FunpayWorker` and spawns asyncio task
3. Worker starts sync polling thread, events flow through queue
4. Worker handles `NEW_MESSAGE` events by calling AI service (incomplete)
5. `/ai/stop` cancels all worker tasks

**Repository Pattern**:
- Base repository in `src/repositories/base_repository.py`
- Concrete repos: `UserRepository`, `MessagesRepository`
- Injected via FastAPI dependencies

**Models vs Schemas**:
- `src/models/`: SQLAlchemy ORM models (User, Messages, ApiPolling)
- `src/schemas/`: Pydantic models for validation (WorkerState, auth schemas)

## Known Issues & Incomplete Features

- AI integration is stubbed: `AiApi.send_message()` is abstract, `OllamaApi` incomplete
- `/ai/stop` stops all workers instead of per-user
- Authentication routes are commented out
- `FunpayWorker._handle_event()` prints to console instead of proper logging for messages
- No tests present
- Telegram bot is standalone, not integrated with FastAPI lifecycle

## Dependencies

- **fastapi**: Web framework
- **funpayapi**: FunPay marketplace API client (sync library)
- **aiogram**: Telegram bot framework
- **sqlalchemy**: ORM with async support
- **alembic**: Database migrations
- **uvicorn**: ASGI server
