from typing import Literal

from api.v1.base.service import BaseService
from api.v1.notification.schemas import (
    NotificationBase,
    NotificationResponse
)


class NotificationService(BaseService):
    NOTIFICATION_KEY_PREFIX = "notifications"
    MAX_NOTIFICATIONS = 100  # Максимальное количество уведомлений на пользователя

    async def _get_notification_key(self, telegram_id: int) -> str:
        """Получить ключ для списка уведомлений пользователя"""
        return f"{self.NOTIFICATION_KEY_PREFIX}:{telegram_id}"

    async def _get_unread_count_key(self, telegram_id: int) -> str:
        """Получить ключ для счетчика непрочитанных уведомлений"""
        return f"{self.NOTIFICATION_KEY_PREFIX}:unread:{telegram_id}"

    async def create_notification(
        self,
        telegram_id: int,
        notification_type: Literal["operation_status", "referral_deposit", "referral_join"],
        title: str,
        message: str,
        image_url: str | None = None,
        detail_image_url: str | None = None,
        **extra_data
    ) -> dict:
        """Создать уведомление для пользователя."""
        result = await self._send_notification(
            telegram_id=telegram_id,
            notification_type=notification_type,
            title=title,
            message=message,
            max_notifications=self.MAX_NOTIFICATIONS,
            image_url=image_url,
            detail_image_url=detail_image_url,
            **extra_data
        )
        return result or {}

    async def create_operation_status_notification(
        self,
        telegram_id: int,
        operation_id: str,
        operation_status: str,
        amount: float | None = None,
        image_url: str | None = None,
        detail_image_url: str | None = None,
    ) -> dict:
        """Создать уведомление об изменении статуса операции"""
        title = "Статус операции изменен"
        message = f"Статус операции {operation_id[:8]} изменен на {operation_status}"
        if amount:
            message += f" на сумму {amount} USDt"

        return await self.create_notification(
            telegram_id=telegram_id,
            notification_type="operation_status",
            title=title,
            message=message,
            image_url=image_url,
            detail_image_url=detail_image_url,
            operation_id=operation_id,
            operation_status=operation_status,
            amount=amount,
        )

    async def create_referral_deposit_notification(
        self,
        telegram_id: int,
        amount: float,
        source_referral_id: int | None = None,
        source_username: str | None = None,
        image_url: str | None = None,
        detail_image_url: str | None = None,
    ) -> dict:
        """Создать уведомление о начислении на реферальный баланс"""
        title = "Начисление на реферальный баланс"
        if source_username:
            message = f"Начислено {amount} USDt от реферала @{source_username}"
        elif source_referral_id:
            message = f"Начислено {amount} USDt от реферала {source_referral_id}"
        else:
            message = f"Начислено {amount} USDt на реферальный баланс"

        return await self.create_notification(
            telegram_id=telegram_id,
            notification_type="referral_deposit",
            title=title,
            message=message,
            image_url=image_url,
            detail_image_url=detail_image_url,
            amount=amount,
            source_referral_id=source_referral_id,
            source_username=source_username,
        )

    async def create_referral_join_notification(
        self,
        telegram_id: int,
        referral_id: int,
        referral_username: str | None = None,
        image_url: str | None = None,
        detail_image_url: str | None = None,
    ) -> dict:
        """Создать уведомление о присоединении через реферальную ссылку"""
        title = "Новый реферал"
        if referral_username:
            message = f"К вам присоединился реферал @{referral_username}"
        else:
            message = f"К вам присоединился новый реферал {referral_id}"

        return await self.create_notification(
            telegram_id=telegram_id,
            notification_type="referral_join",
            title=title,
            message=message,
            image_url=image_url,
            detail_image_url=detail_image_url,
            referral_id=referral_id,
            referral_username=referral_username,
        )

    async def get_notifications(
        self,
        telegram_id: int,
        limit: int | None = None,
        offset: int | None = None
    ) -> NotificationResponse:
        """Получить уведомления пользователя с пагинацией"""
        if not self.redis:
            return NotificationResponse(
                notifications=[],
                total=0,
                unread_count=0,
                limit=limit,
                offset=offset
            )

        notification_key = await self._get_notification_key(telegram_id)
        
        # Получаем все уведомления
        all_notifications = await self.redis.lrange_json(notification_key)
        total = len(all_notifications)

        # Применяем пагинацию
        if offset is not None and limit is not None:
            notifications = all_notifications[offset:offset + limit]
        elif offset is not None:
            notifications = all_notifications[offset:]
        elif limit is not None:
            notifications = all_notifications[:limit]
        else:
            notifications = all_notifications

        # Подсчитываем непрочитанные
        unread_count = sum(1 for n in all_notifications if not n.get("read", False))
        
        # Обновляем счетчик непрочитанных
        unread_key = await self._get_unread_count_key(telegram_id)
        await self.redis.set(unread_key, str(unread_count))

        return NotificationResponse(
            notifications=[NotificationBase(**n) for n in notifications],
            total=total,
            unread_count=unread_count,
            limit=limit,
            offset=offset
        )

    async def mark_as_read(self, telegram_id: int, notification_ids: list[str]) -> int:
        """Отметить уведомления как прочитанные"""
        if not self.redis:
            return 0

        notification_key = await self._get_notification_key(telegram_id)
        all_notifications = await self._get_all_notifications(notification_key)
        
        marked_count = 0
        notification_ids_set = set(notification_ids)

        # Обновляем статус прочитанных уведомлений
        for notification in all_notifications:
            if notification["notification_id"] in notification_ids_set and not notification.get("read", False):
                notification["read"] = True
                marked_count += 1

        # Обновляем список в Redis
        if marked_count > 0:
            await self._update_notifications(notification_key, all_notifications)
            
            # Обновляем счетчик непрочитанных
            unread_key = await self._get_unread_count_key(telegram_id)
            current_unread = await self.redis.get(unread_key)
            if current_unread:
                new_unread = max(0, int(current_unread) - marked_count)
                await self.redis.set(unread_key, str(new_unread))

        return marked_count

    async def _get_all_notifications(self, notification_key: str) -> list[dict]:
        """Получить все уведомления из Redis"""
        if not self.redis:
            return []
        return await self.redis.lrange_json(notification_key)

    async def _update_notifications(self, notification_key: str, notifications: list[dict]):
        """Обновить список уведомлений в Redis"""
        if not self.redis:
            return
        
        # Удаляем старый список
        await self.redis.delete(notification_key)
        
        # Добавляем обновленные уведомления
        for notification in reversed(notifications):  # Сохраняем порядок (новые в начале)
            await self.redis.lpush_json(notification_key, notification)

