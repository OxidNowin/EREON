from uuid import UUID
from typing import Sequence
from decimal import Decimal

from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

from infra.postgres.models import Operation, Wallet
from infra.postgres.models.operation import OperationStatus, OperationType
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
            .options(selectinload(self.model_cls.crypto_replenishment))
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
            .join(Wallet, Operation.wallet_id == Wallet.wallet_id)
            .where(Wallet.telegram_id == telegram_id)
            .order_by(self.model_cls.created_at.desc())
            .options(selectinload(self.model_cls.crypto_replenishment))
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def get_operation(self, operation_id: UUID) -> Operation | None:
        stmt = (
            select(self.model_cls)
            .where(self.model_cls.operation_id == operation_id)
            .options(selectinload(self.model_cls.crypto_replenishment))
        )
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

    async def get_total_referrals_spending(self, ids: Sequence[int]) -> Decimal:
        stmt = (
            select(func.coalesce(func.sum(Operation.total_amount), Decimal("0")))
            .select_from(Operation)
            .join(Wallet, Operation.wallet_id == Wallet.wallet_id)
            .where(
                Wallet.telegram_id.in_(ids),
                Operation.status == OperationStatus.CONFIRMED
            )
        )
        result = await self._db.execute(stmt)
        return result.scalar() or Decimal("0")

    async def get_user_total_spending(self, telegram_id: int) -> Decimal:
        """Получает общую сумму потраченных средств пользователем (только успешные операции списания)"""
        stmt = (
            select(func.coalesce(func.sum(Operation.total_amount), Decimal("0")))
            .select_from(Operation)
            .join(Wallet, Operation.wallet_id == Wallet.wallet_id)
            .where(
                Wallet.telegram_id == telegram_id,
                Operation.status == OperationStatus.CONFIRMED,
                Operation.operation_type == OperationType.WITHDRAW
            )
        )
        result = await self._db.execute(stmt)
        return result.scalar() or Decimal("0")
