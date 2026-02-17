import uuid
from dataclasses import dataclass
from datetime import datetime
from logging import getLogger
from typing import Literal

from crypto_processing.client import CryptoProcessingClient
from infra.postgres.uow import PostgresUnitOfWork
from infra.redis.redis_api import RedisAPI
from banking.abstractions import IBankPaymentClient

logger = getLogger(__name__)


@dataclass
class BaseService:
    uow: PostgresUnitOfWork
    crypto_processing_client: CryptoProcessingClient | None = None
    redis: RedisAPI | None = None
    bank_client: IBankPaymentClient | None = None

    async def _send_notification(
        self,
        telegram_id: int,
        notification_type: Literal["operation_status", "referral_deposit", "referral_join"],
        title: str,
        message: str,
        max_notifications: int = 100,
        image_url: str | None = None,
        detail_image_url: str | None = None,
        **extra_data
    ) -> dict | None:
        """Вспомогательный метод для отправки уведомлений через Redis."""
        if not self.redis:
            return None

        notification_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()

        notification_data = {
            "notification_id": notification_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "created_at": created_at,
            "read": False,
            "image_url": image_url,
            "detail_image_url": detail_image_url,
            **extra_data
        }

        notification_key = f"notifications:{telegram_id}"
        await self.redis.lpush_json(notification_key, notification_data)

        unread_key = f"notifications:unread:{telegram_id}"
        await self.redis.incr(unread_key)

        length = await self.redis.llen(notification_key)
        if length > max_notifications:
            await self.redis.ltrim(notification_key, 0, max_notifications - 1)

        return notification_data

    async def _safe_notify_operation_status(
        self,
        telegram_id: int,
        operation_id: str,
        operation_status: str,
        amount: float | None = None,
    ) -> None:
        """Безопасная отправка уведомления об изменении статуса операции."""
        try:
            title = "Статус операции изменен"
            message = f"Статус операции {operation_id[:8]} изменен на {operation_status}"
            if amount is not None:
                message += f" на сумму {amount} USDt"

            await self._send_notification(
                telegram_id=telegram_id,
                notification_type="operation_status",
                title=title,
                message=message,
                operation_id=operation_id,
                operation_status=operation_status,
                amount=amount,
            )
        except Exception as e:
            logger.error("Ошибка при отправке уведомления о статусе операции: %s", e, exc_info=True)

    async def _safe_notify_referral_deposit(
        self,
        telegram_id: int,
        amount: float,
        source_referral_id: int | None = None,
        source_username: str | None = None,
    ) -> None:
        """Безопасная отправка уведомления о начислении на реферальный баланс."""
        try:
            title = "Начисление на реферальный баланс"
            if source_referral_id:
                message = f"Начислено {amount} USDt от реферала {source_referral_id}"
            else:
                message = f"Начислено {amount} USDt на реферальный баланс"

            await self._send_notification(
                telegram_id=telegram_id,
                notification_type="referral_deposit",
                title=title,
                message=message,
                amount=amount,
                source_referral_id=source_referral_id,
                source_username=source_username,
            )
        except Exception as e:
            logger.error("Ошибка при отправке уведомления о реферальном начислении: %s", e, exc_info=True)

    async def _safe_notify_referral_join(
        self,
        telegram_id: int,
        referral_id: int,
        referral_username: str | None = None,
    ) -> None:
        """Безопасная отправка уведомления о присоединении реферала."""
        try:
            title = "Новый реферал"
            if referral_username:
                message = f"К вам присоединился реферал @{referral_username}"
            else:
                message = f"К вам присоединился новый реферал {referral_id}"

            await self._send_notification(
                telegram_id=telegram_id,
                notification_type="referral_join",
                title=title,
                message=message,
                referral_id=referral_id,
                referral_username=referral_username,
            )
        except Exception as e:
            logger.error("Ошибка при отправке уведомления о присоединении реферала: %s", e, exc_info=True)
