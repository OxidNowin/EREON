from typing import Sequence

from sqlalchemy import select, literal

from infra.postgres.models.wallet import Wallet
from infra.postgres.storage.base_storage import PostgresStorage


class WalletStorage(PostgresStorage[Wallet]):
    model_cls = Wallet

    async def get_wallet_by_address(self, address: str) -> Wallet | None:
        stmt = select(self.model_cls).where(
            literal(address) == self.model_cls.addresses.any()
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_wallets(self, telegram_id: int) -> Sequence[Wallet]:
        stmt = select(self.model_cls).where(self.model_cls.telegram_id == telegram_id)
        result = await self._db.execute(stmt)
        return result.scalars().all()
