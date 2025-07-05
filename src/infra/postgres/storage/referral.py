from typing import Sequence
from sqlalchemy import select

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
