from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal
from uuid import UUID


class NotificationType:
    """Типы уведомлений"""
    OPERATION_STATUS = "operation_status"  # Изменение статуса операции
    REFERRAL_DEPOSIT = "referral_deposit"  # Начисление на баланс реферала
    REFERRAL_JOIN = "referral_join"  # Присоединение через реферальную ссылку


class NotificationBase(BaseModel):
    notification_id: str = Field(..., description="Уникальный ID уведомления")
    type: Literal["operation_status", "referral_deposit", "referral_join"] = Field(
        ..., 
        description="Тип уведомления"
    )
    title: str = Field(..., description="Заголовок уведомления")
    message: str = Field(..., description="Текст уведомления")
    created_at: str = Field(..., description="Дата создания уведомления (ISO format)")
    read: bool = Field(default=False, description="Прочитано ли уведомление")
    image_url: str | None = Field(None, description="URL превью-картинки уведомления")
    detail_image_url: str | None = Field(None, description="URL детальной картинки уведомления")
    action_url: str | None = Field(None, description="URL для кнопки действия (например, «Ознакомиться»)")
    action_label: str | None = Field(None, description="Текст кнопки действия; если не задан — используется дефолтный")


class OperationStatusNotification(NotificationBase):
    type: Literal["operation_status"] = "operation_status"
    operation_id: UUID = Field(..., description="ID операции")
    operation_status: str = Field(..., description="Новый статус операции")
    amount: float | None = Field(None, description="Сумма операции")


class ReferralDepositNotification(NotificationBase):
    type: Literal["referral_deposit"] = "referral_deposit"
    amount: float = Field(..., description="Сумма начисления")
    source_referral_id: int | None = Field(None, description="ID реферала, который начислил")
    source_username: str | None = Field(None, description="Username реферала, который начислил")


class ReferralJoinNotification(NotificationBase):
    type: Literal["referral_join"] = "referral_join"
    referral_id: int = Field(..., description="ID присоединившегося реферала")
    referral_username: str | None = Field(None, description="Username присоединившегося реферала")


class NotificationResponse(BaseModel):
    notifications: list[NotificationBase] = Field(..., description="Список уведомлений")
    total: int = Field(..., description="Общее количество уведомлений")
    unread_count: int = Field(..., description="Количество непрочитанных уведомлений")
    limit: int | None = Field(None, description="Лимит на страницу")
    offset: int | None = Field(None, description="Смещение")


class MarkAsReadRequest(BaseModel):
    notification_ids: list[str] = Field(..., description="Список ID уведомлений для отметки как прочитанные")

