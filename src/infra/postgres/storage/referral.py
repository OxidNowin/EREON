from typing import Sequence
from sqlalchemy import select, update

from infra.postgres.models.referral import Referral
from infra.postgres.storage.base_storage import PostgresStorage


class ReferralStorage(PostgresStorage[Referral]):
    model_cls = Referral

    async def get_id_by_referral_code(self, code: str) -> int | None:
        stmt = select(self.model_cls.telegram_id).where(self.model_cls.code == code)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_referrals_of_user(self, user_id: int) -> Sequence[Referral]:
        stmt = select(self.model_cls).where(self.model_cls.referred_by == user_id)
        result = await self._db.execute(stmt)
        return result.scalars().all()

    async def update(self, telegram_id: int, **fields_to_update) -> bool:
        """Универсальный метод для обновления полей реферала"""
        stmt = (
            update(self.model_cls)
            .where(self.model_cls.telegram_id == telegram_id)
            .values(**fields_to_update)
            .returning(self.model_cls.telegram_id)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_referred_users(self, telegram_id: int) -> Sequence[Referral]:
        stmt = select(self.model_cls).where(self.model_cls.referred_by == telegram_id)
        result = await self._db.execute(stmt)
        return result.scalars().all()
