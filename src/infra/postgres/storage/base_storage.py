from typing import Generic, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from infra.postgres.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class PostgresStorage(Generic[ModelT]):

    model_cls: Type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        self._db: AsyncSession = db
