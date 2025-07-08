from uuid import UUID

from api.v1.base.service import BaseService
from api.v1.wallet.schemas import WalletResponse, WalletCurrencyList
from infra.postgres.models import WalletCurrency


class WalletService(BaseService):
    _cached_currencies: WalletCurrencyList | None = None

    async def get_wallet(self, wallet_id: UUID) -> WalletResponse:
        wallet = await self.uow.wallet.get_by_id(wallet_id)
        if not wallet:
            raise
        return WalletResponse.model_validate(wallet)

    async def get_wallets(self, telegram_id: int) -> list[WalletResponse]:
        wallets = await self.uow.wallet.get_user_wallets(telegram_id)
        if not wallets:
            raise
        return [WalletResponse.model_validate(wallet) for wallet in wallets]

    @classmethod
    def get_currencies(cls) -> WalletCurrencyList:
        if cls._cached_currencies is None:
            cls._cached_currencies = WalletCurrencyList(
                currencies=[c.value for c in WalletCurrency]
            )
        return cls._cached_currencies
