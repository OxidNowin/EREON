from uuid import UUID
from typing import Sequence

from sqlalchemy import select, update

from infra.postgres.models import Operation, Wallet
from infra.postgres.storage.base_storage import PostgresStorage


class OperationStorage(PostgresStorage[Operation]):
    model_cls = Operation

    async def get_wallet_operations(
            self,
            wallet_id: UUID,
            limit: int | None = None,
            offset: int | None = None,
    ) -> Sequence[Operation]:
        stmt = (
            select(self.model_cls)
            .where(self.model_cls.wallet_id == wallet_id)
            .order_by(self.model_cls.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def get_user_operations(
            self,
            telegram_id: int,
            limit: int | None = None,
            offset: int | None = None,
    ) -> Sequence[Operation]:
        stmt = (
            select(self.model_cls)
            .join(self.model_cls.wallet)
            .where(Wallet.telegram_id == telegram_id)
            .order_by(self.model_cls.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def get_operation(self, operation_id: UUID) -> Operation | None:
        stmt = select(self.model_cls).where(self.model_cls.operation_id == operation_id)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_operation(self, operation_id: UUID, **fields_to_update) -> bool:
        stmt = (
            update(self.model_cls)
            .where(self.model_cls.operation_id == operation_id)
            .values(**fields_to_update)
            .returning(self.model_cls.operation_id)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none() is not None
