import asyncio
import dataclasses
import logging
import os
import ssl
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
from typing import AsyncGenerator

from sqlalchemy import DateTime, Enum, Integer, and_, event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    Mapped,
    Session,
    declarative_base,
    mapped_column,
    with_loader_criteria,
)

from config import get_config


Base = declarative_base()


def enum_as_str(enum_cls):
    return Enum(
        enum_cls,
        native_enum=False,
        create_constraint=False,
        validate_strings=True,
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    deleted_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    @classmethod
    def not_deleted(cls):
        return cls.deleted_at.is_(None)

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(tz=timezone.utc)


@dataclasses.dataclass(frozen=True)
class DBSettings:
    database_url: str

    db_engine_pool_pre_ping: bool = True
    db_engine_pool_size: int = (
        5 if get_config().general.environment != "production" else 10
    )
    db_engine_max_overflow: int = (
        20 if get_config().general.environment != "production" else 20
    )
    db_engine_pool_timeout: int = 15

    sql_engine_echo: bool = False


class SQLAlchemyManager:
    logger = logging.getLogger("sqlalchemy")
    _engine: AsyncEngine | None = None
    _sessionmaker: async_sessionmaker[AsyncSession] | None = None

    @classmethod
    def get_async_engine(cls, settings: DBSettings) -> AsyncEngine:
        if cls._engine is not None:
            return cls._engine

        ssl_cert_path = os.getenv("SSL_CERT_PATH")
        cls.logger.info("SSL_CERT_PATH: %s", ssl_cert_path)

        app_name = f"appss-back:{os.getenv('HOSTNAME', 'unknown')}"

        connect_args = {
            "server_settings": {"application_name": app_name},
            "command_timeout": 60,
        }

        db_url = settings.database_url
        if ssl_cert_path and os.path.exists(ssl_cert_path):
            if "?sslmode=" in db_url:
                db_url = db_url.split("?sslmode=")[0]

            ctx = ssl.create_default_context(cafile=ssl_cert_path)
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.check_hostname = True
            connect_args["ssl"] = ctx

        cls.logger.info("Create async engine", extra=dataclasses.asdict(settings))

        cls._engine = create_async_engine(
            db_url,
            pool_pre_ping=settings.db_engine_pool_pre_ping,
            pool_size=settings.db_engine_pool_size,
            max_overflow=settings.db_engine_max_overflow,
            pool_timeout=settings.db_engine_pool_timeout,
            pool_recycle=1800,
            echo=settings.sql_engine_echo,
            connect_args=connect_args,
        )
        return cls._engine

    @classmethod
    def get_sessionmaker(cls, settings: DBSettings) -> async_sessionmaker[AsyncSession]:
        if cls._sessionmaker is not None:
            return cls._sessionmaker

        engine = cls.get_async_engine(settings)
        cls._sessionmaker = async_sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )
        return cls._sessionmaker


db_settings = DBSettings(database_url=get_config().db.url)
SessionLocal = SQLAlchemyManager.get_sessionmaker(db_settings)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = SessionLocal()
    try:
        yield session
        if session.in_transaction():
            await asyncio.shield(session.commit())
    except BaseException:
        with suppress(Exception):
            await asyncio.shield(session.rollback())
        raise
    finally:
        with suppress(Exception):
            await asyncio.shield(session.close())


@asynccontextmanager
async def get_session_direct() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = SessionLocal()
    try:
        yield session
        if session.in_transaction():
            await asyncio.shield(session.commit())
    except BaseException:
        with suppress(Exception):
            await asyncio.shield(session.rollback())
        raise
    finally:
        with suppress(Exception):
            await asyncio.shield(session.close())


def _soft_delete_normal(cls):
    cond = cls.deleted_at.is_(None)
    if hasattr(cls, "published_at"):
        cond = and_(cond, cls.published_at.is_not(None))
    return cond


def _soft_delete_include_unpublished(cls):
    return cls.deleted_at.is_(None)


def _soft_delete_deleted_only(cls):
    return cls.deleted_at.is_not(None)


SOFT_DELETE_OPT_NORMAL = with_loader_criteria(
    SoftDeleteMixin,
    _soft_delete_normal,
    include_aliases=True,
    propagate_to_loaders=True,
)

SOFT_DELETE_OPT_INCLUDE_UNPUBLISHED = with_loader_criteria(
    SoftDeleteMixin,
    _soft_delete_include_unpublished,
    include_aliases=True,
    propagate_to_loaders=True,
)

SOFT_DELETE_OPT_DELETED_ONLY = with_loader_criteria(
    SoftDeleteMixin,
    _soft_delete_deleted_only,
    include_aliases=True,
    propagate_to_loaders=True,
)


@event.listens_for(Session, "do_orm_execute")
def _add_soft_delete_filter(execute_state):
    if not execute_state.is_select or execute_state.is_relationship_load:
        return

    include_unpublished = execute_state.execution_options.get(
        "include_unpublished", False
    )
    deleted_only = execute_state.execution_options.get("include_deleted", False)

    with_deleted = execute_state.execution_options.get("with_deleted", False)

    if deleted_only:
        opt = SOFT_DELETE_OPT_DELETED_ONLY
    elif with_deleted:
        return
    else:
        opt = (
            SOFT_DELETE_OPT_INCLUDE_UNPUBLISHED
            if include_unpublished
            else SOFT_DELETE_OPT_NORMAL
        )

    execute_state.statement = execute_state.statement.options(opt)