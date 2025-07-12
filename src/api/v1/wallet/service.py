from uuid import UUID

from api.v1.base.service import BaseService
from api.v1.wallet.schemas import WalletCurrencyList
from infra.postgres.models import WalletCurrency, Wallet


class WalletService(BaseService):
    _cached_currencies: WalletCurrencyList | None = None

    async def get_wallet(self, wallet_id: UUID) -> Wallet:
        wallet = await self.uow.wallet.get_by_id(wallet_id)
        if not wallet:
            raise
        return wallet

    async def get_wallets(self, telegram_id: int) -> list[Wallet]:
        wallets = await self.uow.wallet.get_user_wallets(telegram_id)
        if not wallets:
            raise
        return wallets

    @classmethod
    def get_currencies(cls) -> WalletCurrencyList:
        if cls._cached_currencies is None:
            cls._cached_currencies = WalletCurrencyList(
                currencies=[c.value for c in WalletCurrency]
            )
        return cls._cached_currencies
