from typing import TypeVar, TypeAlias, Any, Optional

from collections.abc import Iterable

from sqlalchemy.sql import Select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar("T")

ModelType = TypeVar("ModelType")
Statement: TypeAlias = Any


class AsyncSessionUtil:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(
        self, stmt: Statement, params: Optional[Any] = None, **kwargs: Any
    ) -> Result:
        if params is None:
            return await self.session.execute(stmt, **kwargs)
        return await self.session.execute(stmt, params, **kwargs)

    async def one(self, stmt: Select) -> ModelType | None:
        return (await self.execute(stmt)).scalars().one_or_none()

    async def first(self, stmt: Select) -> ModelType | None:
        return (await self.execute(stmt)).scalars().first()

    async def all(self, stmt: Select) -> list[ModelType]:
        return (await self.session.execute(stmt)).scalars().unique().all()

    def add(self, obj: ModelType) -> None:
        self.session.add(obj)

    def add_batch(self, obj_list: list[ModelType]) -> None:
        self.session.add_all(obj_list)

    async def delete(self, obj: ModelType) -> None:
        await self.session.delete(obj)

    async def refresh(self, obj: ModelType, attrs: Iterable[str]) -> None:
        await self.session.refresh(obj, attrs)

    async def flush(self, objs: Iterable[ModelType] | None = None) -> None:
        await self.session.flush(objs)

    async def save(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def batch_save(self, objs: list[ModelType]) -> None:
        self.add_batch(objs)
        await self.session.flush()

    async def _commit(self) -> None:
        await self.session.commit()
