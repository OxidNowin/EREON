from sqlalchemy import select, update

from infra.postgres.models import CryptocurrencyReplenishment
from infra.postgres.storage.base_storage import PostgresStorage


class CryptocurrencyReplenishmentStorage(PostgresStorage[CryptocurrencyReplenishment]):
    model_cls = CryptocurrencyReplenishment

    async def get_by_tx_id(self, tx_id: str) -> CryptocurrencyReplenishment | None:
        stmt = select(self.model_cls).where(self.model_cls.tx_id == tx_id)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()
