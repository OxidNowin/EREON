from uuid import UUID
from typing import Sequence

from sqlalchemy import select, and_, update

from infra.postgres.models import Operation, OperationStatus
from infra.postgres.storage.base_storage import PostgresStorage


class OperationStorage(PostgresStorage[Operation]):
    model_cls = Operation

    async def get_wallet_operations(self, wallet_id: UUID) -> Sequence[Operation]:
        stmt = (
            select(self.model_cls)
            .where(
                and_(
                    self.model_cls.wallet_id == wallet_id,
                    self.model_cls.status == OperationStatus.CONFIRMED,
                )
            )
            .order_by(self.model_cls.created_at.desc())
        )
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def update_operation(self, operation_id: UUID, **fields_to_update) -> bool:
        stmt = (
            update(self.model_cls)
            .where(self.model_cls.operation_id == operation_id)
            .values(**fields_to_update)
            .returning(self.model_cls.operation_id)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none() is not None
