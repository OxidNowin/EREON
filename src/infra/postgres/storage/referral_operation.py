from uuid import UUID
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
