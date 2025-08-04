import time
from decimal import Decimal
from uuid import UUID

from api.v1.base.service import BaseService
from api.v1.payment.schemas import SbpPaymentCreate
from banking.providers.alfa import PaymentStatus
from infra.postgres.models import Operation, OperationStatus, OperationType, SbpPayment, SbpPaymentStatus


class PaymentService(BaseService):
    TIME_TO_CHECK: int = 15

    async def create_sbp_payment(
            self,
            user_id: UUID,
            wallet_id: UUID,
            payment_data: SbpPaymentCreate
    ) -> SbpPayment:
        wallet = await self.uow.wallet.get_wallet_by_id_for_update(wallet_id, user_id)
        if not wallet:
            raise

        qrc_id = payment_data.get_qr_id()
        payment_link_data = await self.bank_client.get_payment_link_data(qrc_id)
        crypto_amount = Decimal((payment_link_data.amount * 100) * payment_data.exchange)

        if wallet.balance < crypto_amount:
            raise

        payment_result = await self.bank_client.process_payment(payment_link_data)

        if payment_result.status == PaymentStatus.ERROR.value:
            raise

        crypto_fee = Decimal((payment_result.commission * 100) * payment_data.exchange)
        total_crypto_amount = crypto_fee + crypto_amount

        if payment_result.status == PaymentStatus.COMPLETE.value:
            operation_status = OperationStatus.CONFIRMED
            sbp_payment_status = SbpPaymentStatus.CONFIRMED
        else:
            operation_status = OperationStatus.PENDING
            sbp_payment_status = SbpPaymentStatus.PENDING

        async with self.uow.db.begin_nested():
            operation = await self.uow.operation.add(
                Operation(
                    wallet_id=wallet_id,
                    status=operation_status,
                    operation_type=OperationType.WITHDRAW,
                    amount=crypto_amount,
                    fee=crypto_fee,
                    total_amount=total_crypto_amount,
                )
            )
            sbp_payment = await self.uow.sbp_payment.add(
                SbpPayment(
                    operation_id=operation.id,
                    rub_amount=payment_link_data.amount,
                    fee_rub=payment_result.commission,
                    total_amount_rub=payment_link_data.amount + payment_result.commission,
                    crypto_amount=crypto_amount,
                    fee_crypto=crypto_fee,
                    total_amount_crypto=total_crypto_amount,
                    exchange=payment_data.exchange,
                    sbp_url=str(payment_data.sbp_url),
                    outgoing_payment_id=payment_result.payment_id,
                    status=sbp_payment_status,
                )
            )

        if payment_result.status == PaymentStatus.COMPLETE.value:
            wallet.balance -= total_crypto_amount
            return sbp_payment

        payment_completed = await self.is_payment_completed(payment_result.payment_id)

        if not payment_completed:
            raise
        return sbp_payment


    async def is_payment_completed(self, payment_id: str) -> bool:
        now = time.perf_counter()

        while time.perf_counter() - now < self.TIME_TO_CHECK:
            payment_status = await self.bank_client.get_payment_status(payment_id)

            if payment_status is None:
                continue

            if payment_status.status == PaymentStatus.ERROR.value:
                raise

            if payment_status.status == PaymentStatus.COMPLETE.value:
                return True

        return False
