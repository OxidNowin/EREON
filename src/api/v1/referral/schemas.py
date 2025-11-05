from pydantic import BaseModel, Field
from typing import List
from uuid import UUID

from infra.postgres.models import ReferralType, ReferralOperationType, ReferralOperationStatus


class ReferralTypeSet(BaseModel):
    referral_type: ReferralType = Field(
        ..., 
        description="Тип реферальной программы",
        examples=["FIXED_INCOME", "PERCENTAGE_INCOME"]
    )


class ReferralInfo(BaseModel):
    telegram_id: int = Field(..., description="ID пользователя")
    referred_by: int | None = Field(None, description="ID того, кто пригласил")
    code: str = Field(..., description="Код для приглашения")
    active: bool = Field(..., description="Активен ли реферал")
    referral_type: ReferralType | None = Field(None, description="Тип реферальной программы")
    referral_spending: float = Field(..., description="Денег потрачено при фиксированном типе реферальной программы")
    referral_count: int = Field(..., description="Количество приглашенных людей")
    balance: int = Field(..., description="Баланс реферала")
    referred_users: List[int] = Field(..., description="Список ID приглашенных пользователей")


class ReferralOperationInfo(BaseModel):
    referral_operation_id: UUID = Field(..., description="ID операции")
    status: ReferralOperationStatus = Field(..., description="Статус операции")
    operation_type: ReferralOperationType = Field(..., description="Тип операции")
    amount: float = Field(..., description="Сумма операции")
    created_at: str = Field(..., description="Дата создания")


class ReferralOperationsResponse(BaseModel):
    operations: List[ReferralOperationInfo] = Field(..., description="Список операций")
    total: int = Field(..., description="Общее количество операций")
    limit: int | None = Field(None, description="Лимит на страницу")
    offset: int | None = Field(None, description="Смещение")


class ReferralStatsInfo(BaseModel):
    telegram_id: int = Field(..., description="ID приглашенного пользователя")
    username: str | None = Field(None, description="Username пользователя в Telegram (если доступен)")
    avatar_url: str | None = Field(None, description="URL фото профиля пользователя в Telegram (если доступен)")
    earned_amount: float = Field(..., description="Сумма, полученная от этого реферала")
    percentage: float | None = Field(None, description="Процент от 150 USDt для FIXED_INCOME (сколько осталось до порога), None для PERCENTAGE_INCOME")


class ReferralStatsResponse(BaseModel):
    referrals: List[ReferralStatsInfo] = Field(..., description="Список приглашенных рефералов со статистикой")
    referral_type: ReferralType | None = Field(None, description="Тип реферальной программы")
    total: int = Field(..., description="Общее количество рефералов")
    total_earned: float = Field(..., description="Общая сумма, полученная от всех рефералов")
    limit: int | None = Field(None, description="Лимит на страницу")
    offset: int | None = Field(None, description="Смещение")


class ReferralDepositOperationInfo(BaseModel):
    referral_operation_id: UUID = Field(..., description="ID операции")
    status: ReferralOperationStatus = Field(..., description="Статус операции")
    amount: float = Field(..., description="Сумма операции")
    created_at: str = Field(..., description="Дата создания")
    source_referral_id: int | None = Field(None, description="ID реферала, который начислил эту сумму")
    source_username: str | None = Field(None, description="Username реферала, который начислил")
    source_avatar_url: str | None = Field(None, description="URL фото профиля реферала, который начислил")


class ReferralDepositOperationsResponse(BaseModel):
    operations: List[ReferralDepositOperationInfo] = Field(..., description="Список операций начисления")
    total: int = Field(..., description="Общее количество операций начисления")
    total_referrals: int = Field(..., description="Суммарное количество приглашенных пользователей")
    limit: int | None = Field(None, description="Лимит на страницу")
    offset: int | None = Field(None, description="Смещение")
