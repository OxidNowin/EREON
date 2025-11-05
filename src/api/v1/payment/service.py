import asyncio
import time
from decimal import Decimal
from uuid import UUID
from logging import getLogger

from api.v1.base.service import BaseService
from api.v1.payment.schemas import SbpPaymentCreate
from banking.providers.alfa import PaymentStatus, AlfaApiError
from infra.postgres.models import (
    Operation, OperationStatus, OperationType, SbpPayment, SbpPaymentStatus,
    ReferralType, ReferralOperation, ReferralOperationType, ReferralOperationStatus
)
from api.v1.payment.exceptions import PaymentProcessingError, PaymentLinkError
from api.v1.wallet.exceptions import WalletNotFoundError, InsufficientFundsError

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
            raise WalletNotFoundError(f"Wallet with id {wallet_id} not found for user {user_id}")

        try:
            payment_link_data = await self.bank_client.get_payment_link_data(payment_data.get_qr_id())
        except AlfaApiError:
            raise PaymentLinkError("Getting payment link failed")

        crypto_amount = (Decimal(payment_link_data.amount) / 100) / Decimal(payment_data.exchange)

        if wallet.balance < crypto_amount:
            raise InsufficientFundsError(f"Insufficient funds. Required: {crypto_amount}, available: {wallet.balance}")

        try:
            payment_result = await self.bank_client.process_payment(payment_link_data)
        except AlfaApiError:
            raise PaymentProcessingError("Payment processing failed")

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
            # Обработка реферальных начислений
            try:
                await self._process_referral_rewards(wallet.telegram_id, crypto_fee)
            except Exception as e:
                logger.error(f"Ошибка при обработке реферальных начислений: {e}", exc_info=True)
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
        
        # Обработка реферальных начислений
        try:
            await self._process_referral_rewards(wallet.telegram_id, crypto_fee)
        except Exception as e:
            logger.error(f"Ошибка при обработке реферальных начислений: {e}", exc_info=True)
        
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

    def _get_revenue_share_percentage(self, referral_count: int) -> Decimal:
        """
        Возвращает процент Revenue Share в зависимости от количества рефералов:
        - Меньше 3 рефералов: 20%
        - Меньше 5 рефералов: 30%
        - Меньше 8 рефералов: 40%
        - Меньше 10 рефералов: 50%
        - 10 и более: 50%
        """
        if referral_count < 3:
            return Decimal("0.20")  # 20%
        elif referral_count < 5:
            return Decimal("0.30")  # 30%
        elif referral_count < 8:
            return Decimal("0.40")  # 40%
        elif referral_count < 10:
            return Decimal("0.50")  # 50%
        else:
            return Decimal("0.50")  # 50%

    async def _process_referral_rewards(self, telegram_id: int, commission: Decimal) -> None:
        """
        Обрабатывает реферальные начисления после успешной операции.
        
        Логика:
        - CPA (FIXED_INCOME): Начисляет 5 USDt за каждого пользователя, который потратил >= 150 USDt
        - Revenue Share (PERCENTAGE_INCOME): Начисляет процент от комиссии в зависимости от количества рефералов
        """
        # Получаем информацию о реферале пользователя
        user_referral = await self.uow.referral.get_by_id(telegram_id)
        if not user_referral or not user_referral.referred_by:
            return  # У пользователя нет реферала
        
        # Получаем информацию о реферале того, кто пригласил
        referrer_referral = await self.uow.referral.get_by_id(user_referral.referred_by)
        if not referrer_referral or not referrer_referral.type:
            return  # У реферала не установлен тип программы
        
        # CPA (Фиксированная доходность)
        if referrer_referral.type == ReferralType.FIXED_INCOME:
            await self._process_cpa_reward(user_referral.referred_by, telegram_id)
        
        # Revenue Share (Процентная доходность)
        elif referrer_referral.type == ReferralType.PERCENTAGE_INCOME:
            await self._process_revenue_share_reward(
                user_referral.referred_by,
                telegram_id,  # source_referral_id
                commission,
                referrer_referral.referral_count
            )

    async def _process_cpa_reward(self, referrer_id: int, user_id: int) -> None:
        """
        Обрабатывает CPA начисление (5 USDt за каждого пользователя, потратившего >= 150 USDt).
        Начисляет бонус только один раз за каждого пользователя, достигшего порога.
        """
        CPA_THRESHOLD = Decimal("150.0")  # 150 USDt
        CPA_REWARD = Decimal("5.0")  # 5 USDt
        
        # Проверяем общую сумму потраченных средств пользователем
        total_spending = await self.uow.operation.get_user_total_spending(user_id)
        
        if total_spending < CPA_THRESHOLD:
            return  # Пользователь еще не потратил достаточно
        
        # Получаем все рефералов и проверяем, сколько из них потратили >= 150 USDt
        referred_users = await self.uow.referral.get_referred_users(referrer_id)
        
        # Подсчитываем количество рефералов, которые потратили >= 150 USDt
        qualified_users_count = 0
        for referred_user in referred_users:
            user_spending = await self.uow.operation.get_user_total_spending(referred_user.telegram_id)
            if user_spending >= CPA_THRESHOLD:
                qualified_users_count += 1
        
        if qualified_users_count == 0:
            return  # Нет квалифицированных пользователей
        
        # Подсчитываем количество CPA бонусов (операции на 5 USDt)
        referral_operations = await self.uow.referral_operation.get_referral_operations(referrer_id)
        cpa_bonus_count = sum(
            1 for op in referral_operations
            if (op.amount == CPA_REWARD and 
                op.operation_type == ReferralOperationType.DEPOSIT and
                op.status == ReferralOperationStatus.CONFIRMED)
        )
        
        # Если количество бонусов меньше количества квалифицированных пользователей, начисляем
        if cpa_bonus_count < qualified_users_count:
            await self._add_referral_reward(
                referrer_id, 
                CPA_REWARD, 
                ReferralOperationType.DEPOSIT,
                source_referral_id=user_id
            )

    async def _process_revenue_share_reward(
        self, 
        referrer_id: int,
        source_referral_id: int,
        commission: Decimal, 
        referral_count: int
    ) -> None:
        """
        Обрабатывает Revenue Share начисление (процент от комиссии).
        """
        if commission <= 0:
            return  # Нет комиссии для начисления
        
        # Получаем процент в зависимости от количества рефералов
        percentage = self._get_revenue_share_percentage(referral_count)
        
        # Вычисляем сумму начисления
        reward_amount = commission * percentage
        
        # Начисляем бонус
        await self._add_referral_reward(
            referrer_id, 
            reward_amount, 
            ReferralOperationType.DEPOSIT,
            source_referral_id=source_referral_id
        )

    async def _add_referral_reward(
        self, 
        referrer_id: int, 
        amount: Decimal, 
        operation_type: ReferralOperationType,
        source_referral_id: int | None = None
    ) -> None:
        """
        Добавляет реферальное начисление и обновляет баланс реферала.
        
        Args:
            referrer_id: ID реферера, которому начисляется бонус
            amount: Сумма начисления
            operation_type: Тип операции
            source_referral_id: ID реферала, от которого пришла эта операция (опционально)
        """
        # Создаем операцию реферального начисления
        referral_operation = ReferralOperation(
            referral_id=referrer_id,
            source_referral_id=source_referral_id,
            status=ReferralOperationStatus.CONFIRMED,
            operation_type=operation_type,
            amount=amount
        )
        await self.uow.referral_operation.add(referral_operation)
        
        # Обновляем баланс реферала (balance хранится как int, конвертируем Decimal в int)
        # Предполагаем, что balance хранится в минимальных единицах (например, центах)
        # Для USDt: 1 USDt = 1000000 (6 знаков после запятой)
        referrer_referral = await self.uow.referral.get_by_id(referrer_id)
        if referrer_referral:
            # Конвертируем Decimal в int (умножаем на 1000000 для 6 знаков после запятой)
            amount_int = int(amount * Decimal("1000000"))
            new_balance = referrer_referral.balance + amount_int
            await self.uow.referral.update(referrer_id, balance=new_balance)
