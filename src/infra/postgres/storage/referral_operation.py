from uuid import UUID
from decimal import Decimal
from typing import Sequence
from sqlalchemy import select, update, func

from infra.postgres.models import ReferralOperation, Referral
from infra.postgres.storage.base_storage import PostgresStorage


class ReferralOperationStorage(PostgresStorage[ReferralOperation]):
    model_cls = ReferralOperation

    async def get_referral_operations(
            self,
            referral_id: int,
            limit: int | None = None,
            offset: int | None = None,
    ) -> Sequence[ReferralOperation]:
        stmt = (
            select(self.model_cls)
            .where(self.model_cls.referral_id == referral_id)
            .order_by(self.model_cls.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def get_referrer_operations(
            self,
            telegram_id: int,
            limit: int | None = None,
            offset: int | None = None,
    ) -> Sequence[ReferralOperation]:
        stmt = (
            select(self.model_cls)
            .join(Referral, Referral.telegram_id == self.model_cls.referral_id)
            .where(Referral.referred_by == telegram_id)
            .order_by(self.model_cls.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def update_referral_operation(self, referral_operation_id: UUID, **fields_to_update) -> bool:
        stmt = (
            update(self.model_cls)
            .where(self.model_cls.referral_operation_id == referral_operation_id)
            .values(**fields_to_update)
            .returning(self.model_cls.referral_operation_id)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def count_referral_operations(self, referral_id: int) -> int:
        stmt = select(func.count(self.model_cls.referral_operation_id)).where(
            self.model_cls.referral_id == referral_id
        )
        result = await self._db.execute(stmt)
        return result.scalar() or 0

    async def has_cpa_bonus_for_amount(self, referral_id: int, amount: Decimal) -> bool:
        """Проверяет, был ли уже начислен CPA бонус с указанной суммой для реферала"""
        from infra.postgres.models.referral_operation import ReferralOperationType, ReferralOperationStatus
        
        stmt = (
            select(func.count(self.model_cls.referral_operation_id))
            .where(
                self.model_cls.referral_id == referral_id,
                self.model_cls.amount == amount,
                self.model_cls.operation_type == ReferralOperationType.DEPOSIT,
                self.model_cls.status == ReferralOperationStatus.CONFIRMED
            )
        )
        result = await self._db.execute(stmt)
        count = result.scalar() or 0
        return count > 0

    async def get_referrer_total_earned(self, referrer_id: int) -> Decimal:
        """Получает общую сумму, полученную от всех рефералов (начисленную на баланс referrer_id)"""
        from infra.postgres.models.referral_operation import ReferralOperationType, ReferralOperationStatus
        
        stmt = (
            select(func.coalesce(func.sum(self.model_cls.amount), Decimal("0")))
            .where(
                self.model_cls.referral_id == referrer_id,
                self.model_cls.operation_type == ReferralOperationType.DEPOSIT,
                self.model_cls.status == ReferralOperationStatus.CONFIRMED
            )
        )
        result = await self._db.execute(stmt)
        return result.scalar() or Decimal("0")

    async def get_referral_total_earned(self, referrer_id: int, referral_telegram_id: int) -> Decimal:
        """
        Получает сумму, которую принес конкретный реферал на баланс реферера.
        Использует поле source_referral_id для точного определения источника.
        """
        from infra.postgres.models.referral_operation import ReferralOperationType, ReferralOperationStatus
        
        stmt = (
            select(func.coalesce(func.sum(self.model_cls.amount), Decimal("0")))
            .where(
                self.model_cls.referral_id == referrer_id,
                self.model_cls.source_referral_id == referral_telegram_id,
                self.model_cls.operation_type == ReferralOperationType.DEPOSIT,
                self.model_cls.status == ReferralOperationStatus.CONFIRMED
            )
        )
        result = await self._db.execute(stmt)
        return result.scalar() or Decimal("0")

    async def get_deposit_operations_with_source(
        self,
        referral_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[ReferralOperation]:
        """Получает операции начисления (DEPOSIT) с информацией о source_referral_id"""
        from infra.postgres.models.referral_operation import ReferralOperationType
        
        stmt = (
            select(self.model_cls)
            .where(
                self.model_cls.referral_id == referral_id,
                self.model_cls.operation_type == ReferralOperationType.DEPOSIT
            )
            .order_by(self.model_cls.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def count_deposit_operations(self, referral_id: int) -> int:
        """Подсчитывает количество операций начисления (DEPOSIT)"""
        from infra.postgres.models.referral_operation import ReferralOperationType
        
        stmt = (
            select(func.count(self.model_cls.referral_operation_id))
            .where(
                self.model_cls.referral_id == referral_id,
                self.model_cls.operation_type == ReferralOperationType.DEPOSIT
            )
        )
        result = await self._db.execute(stmt)
        return result.scalar() or 0
