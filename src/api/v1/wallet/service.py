from decimal import Decimal
from uuid import UUID

from api.v1.base.service import BaseService
from api.v1.wallet.schemas import WalletCurrencyList, WithdrawRequest
from infra.postgres.models import WalletCurrency, Wallet, Operation, OperationStatus, OperationType


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

    async def withdraw_funds(self, wallet_id: UUID, data: WithdrawRequest) -> Wallet:
        wallet = await self.uow.wallet.get_wallet_by_id_for_update(wallet_id)
        if not wallet:
            raise

        amount = int(data.amount * 1_000_000)
        decimal_amount = Decimal(amount / 1_000_000)

        if wallet.balance < decimal_amount:
            raise

        withdraw_accepted = await self.crypto_processing_client.withdraw_funds(
            address=data.address,
            amount=amount
        )
        if not withdraw_accepted:
            raise

        await self.uow.operation.add(
            Operation(
                wallet_id=wallet_id,
                status=OperationStatus.CONFIRMED,
                operation_type=OperationType.WITHDRAW,
                amount=decimal_amount,
                fee=Decimal(0),
                total_amount=decimal_amount,
            )
        )

        wallet.balance -= decimal_amount
        return wallet

    @classmethod
    def get_currencies(cls) -> WalletCurrencyList:
        if cls._cached_currencies is None:
            cls._cached_currencies = WalletCurrencyList(
                currencies=[c.value for c in WalletCurrency]
            )
        return cls._cached_currencies
