from api.v1.base.service import BaseService
from api.v1.webhook.schemas import CryptocurrencyReplenishmentCreate
from infra.postgres.models import CryptocurrencyReplenishment, Operation, OperationStatus, OperationType
from crypto_processing.network import matcher


class WebhookService(BaseService):
    async def add_balance(self, webhook_data: CryptocurrencyReplenishmentCreate):
        wallet = await self.uow.wallet.get_wallet_by_address_for_update(webhook_data.to_address)
        if not wallet:
            raise ValueError("Wallet not found")

        fee = matcher.get_network_fee(webhook_data.to_address)
        net_amount = webhook_data.amount - fee


        operation = Operation(
            wallet_id=wallet.wallet_id,
            status=OperationStatus.CONFIRMED,
            operation_type=OperationType.DEPOSIT,
            amount=net_amount,
            fee=fee,
            total_amount=webhook_data.amount,
        )
        await self.uow.operation.add(operation)

        replenishment = CryptocurrencyReplenishment(
            operation_id=operation.operation_id,
            **webhook_data.model_dump()
        )
        await self.uow.cryptocurrency_replenishment.add(replenishment)

        wallet.balance += net_amount
