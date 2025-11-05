import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from crypto_processing.client import CryptoProcessingClient
from infra.postgres.uow import PostgresUnitOfWork
from infra.redis.redis_api import RedisAPI
from banking.abstractions import IBankPaymentClient


@dataclass(slots=True)
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
        **extra_data
    ) -> None:
        """Вспомогательный метод для отправки уведомлений через Redis"""
        if not self.redis:
            return

        notification_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()

        notification_data = {
            "notification_id": notification_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "created_at": created_at,
            "read": False,
            **extra_data
        }

        # Добавляем уведомление в начало списка
        notification_key = f"notifications:{telegram_id}"
        await self.redis.lpush_json(notification_key, notification_data)

        # Увеличиваем счетчик непрочитанных
        unread_key = f"notifications:unread:{telegram_id}"
        await self.redis.incr(unread_key)

        # Ограничиваем количество уведомлений
        length = await self.redis.llen(notification_key)
        if length > max_notifications:
            await self.redis.ltrim(notification_key, 0, max_notifications - 1)
