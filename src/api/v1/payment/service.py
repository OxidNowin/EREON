import asyncio
import time
from decimal import Decimal
from uuid import UUID
from logging import getLogger

from api.v1.base.service import BaseService
from api.v1.payment.schemas import SbpPaymentCreate
from banking.providers.alfa import PaymentStatus, AlfaApiError
from infra.postgres.models import Operation, OperationStatus, OperationType, SbpPayment, SbpPaymentStatus

logger = getLogger(__name__)


class PaymentService(BaseService):
    TIME_TO_CHECK: int = 15
    status_map = {
        PaymentStatus.COMPLETE.value: (OperationStatus.CONFIRMED, SbpPaymentStatus.CONFIRMED),
        PaymentStatus.SENDING_MESSAGE.value: (OperationStatus.PENDING, SbpPaymentStatus.PENDING),
        PaymentStatus.ERROR.value: (OperationStatus.CANCELLED, SbpPaymentStatus.CANCELLED),
    }

    async def create_sbp_payment(
            self,
            user_id: UUID,
            wallet_id: UUID,
            payment_data: SbpPaymentCreate
    ) -> SbpPayment:
        wallet = await self.uow.wallet.get_wallet_by_id_for_update(wallet_id, user_id)
        if not wallet:
            raise

        payment_link_data = await self.bank_client.get_payment_link_data(payment_data.get_qr_id())

        crypto_amount = (Decimal(payment_link_data.amount) / 100) / Decimal(payment_data.exchange)

        if wallet.balance < crypto_amount:
            raise

        try:
            payment_result = await self.bank_client.process_payment(payment_link_data)
        except AlfaApiError as e:
            logger.error(e)
            raise

        # TODO add our commission
        crypto_fee = (Decimal(payment_result.commission) / 100) / Decimal(payment_data.exchange)
        total_crypto_amount = crypto_fee + crypto_amount

        operation_status, sbp_payment_status = self.status_map.get(payment_result.status)

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
                operation_id=operation.operation_id,
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
        elif payment_result.status == PaymentStatus.ERROR.value:
            return sbp_payment
        else:
            pass

        payment_completed = await self.is_payment_completed(payment_result.payment_id)

        if not payment_completed:
            operation.status = OperationStatus.CANCELLED
            sbp_payment.status = SbpPaymentStatus.CANCELLED
            return sbp_payment

        wallet.balance -= total_crypto_amount
        operation.status = OperationStatus.CONFIRMED
        sbp_payment.status = SbpPaymentStatus.CONFIRMED
        return sbp_payment

    async def is_payment_completed(self, payment_id: str) -> bool:
        now = time.perf_counter()

        while time.perf_counter() - now < self.TIME_TO_CHECK:
            try:
                payment_status = await self.bank_client.get_payment_status(payment_id)
            except Exception as e:
                logger.error(e)
                payment_status = None

            if payment_status is None:
                continue

            if payment_status.status == PaymentStatus.ERROR.value:
                return False

            if payment_status.status == PaymentStatus.COMPLETE.value:
                return True

            await asyncio.sleep(0.5)

        return False
