from decimal import Decimal, ROUND_DOWN

from api.v1.base.service import BaseService
from api.v1.webhook.schemas import CryptocurrencyReplenishmentCreate
from infra.postgres.models import CryptocurrencyReplenishment, Operation, OperationStatus, OperationType


class WebhookService(BaseService):
    fee_percent = Decimal("5") / Decimal("100")
    fee_exp = Decimal("0.000001")

    async def add_balance(self, webhook_data: CryptocurrencyReplenishmentCreate):
        wallet = await self.uow.wallet.get_wallet_for_update(webhook_data.to_address)
        if not wallet:
            raise ValueError("Wallet not found")

        fee, net_amount = self.get_absolute_fee(webhook_data.amount)

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

    def get_absolute_fee(self, amount: Decimal) -> tuple[Decimal, Decimal]:
        fee = (amount * self.fee_percent).quantize(self.fee_exp, rounding=ROUND_DOWN)
        net_amount = (amount - fee).quantize(self.fee_exp, rounding=ROUND_DOWN)
        return fee, net_amount
