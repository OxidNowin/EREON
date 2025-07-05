from sqlalchemy import select

from infra.postgres.models.wallet import Wallet
from infra.postgres.storage.base_storage import PostgresStorage


class WalletStorage(PostgresStorage[Wallet]):
    model_cls = Wallet

    async def get_wallet_by_token(self, token: str) -> Wallet | None:
        stmt = select(self.model_cls).where(self.model_cls.token == token)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_wallet_by_address(self, address: str) -> Wallet | None:
        stmt = select(self.model_cls).where(self.model_cls.address == address)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()
