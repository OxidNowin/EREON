from typing import Generic, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from infra.postgres.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class PostgresStorage(Generic[ModelT]):

    model_cls: Type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        self._db: AsyncSession = db

    async def add(self, obj: ModelT) -> ModelT:
        self._db.add(obj)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def get_by_id(self, obj_id) -> ModelT | None:
        return await self._db.get(self.model_cls, obj_id)
