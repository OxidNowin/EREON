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
