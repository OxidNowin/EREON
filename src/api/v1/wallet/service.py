from decimal import Decimal
from uuid import UUID

from api.v1.base.service import BaseService
from api.v1.wallet.schemas import WalletCurrencyList, WithdrawRequest
from crypto_processing.network import matcher
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

    async def withdraw_funds(self, wallet_id: UUID, user_id: UUID, data: WithdrawRequest) -> Operation:
        wallet = await self.uow.wallet.get_wallet_by_id_for_update(wallet_id, user_id)
        if not wallet:
            raise

        fee = matcher.get_network_fee(data.address)
        if not fee:
            raise

        amount = int((data.amount + fee) * 1_000_000)
        total_decimal_amount = Decimal(amount / 1_000_000)

        if wallet.balance < total_decimal_amount:
            raise

        withdraw_accepted = await self.crypto_processing_client.withdraw_funds(
            address=data.address,
            amount=amount
        )

        operation = Operation(
            wallet_id=wallet_id,
            status=OperationStatus.CONFIRMED,
            operation_type=OperationType.WITHDRAW,
            amount=data.amount,
            fee=fee,
            total_amount=total_decimal_amount,
        )
        await self.uow.operation.add(operation)
        if not withdraw_accepted:
            operation.status = OperationStatus.CANCELLED
            return operation

        wallet.balance -= total_decimal_amount
        return operation

    @classmethod
    def get_currencies(cls) -> WalletCurrencyList:
        if cls._cached_currencies is None:
            cls._cached_currencies = WalletCurrencyList(
                currencies=[c.value for c in WalletCurrency]
            )
        return cls._cached_currencies
