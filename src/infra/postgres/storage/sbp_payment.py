from uuid import UUID

from sqlalchemy import update

from infra.postgres.models import SbpPayment
from infra.postgres.storage.base_storage import PostgresStorage


class SbpPaymentStorage(PostgresStorage[SbpPayment]):
    model_cls = SbpPayment

    async def update_sbp_payment(self, sbp_payment_id: UUID, **fields_to_update) -> bool:
        stmt = (
            update(self.model_cls)
            .where(self.model_cls.sbp_payment_id == sbp_payment_id)
            .values(**fields_to_update)
            .returning(self.model_cls.sbp_payment_id)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none() is not None
