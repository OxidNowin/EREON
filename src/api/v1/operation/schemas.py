from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from infra.postgres.models import OperationType, OperationStatus


class OperationBase(BaseModel):
    operation_id: UUID = Field(..., description="Уникальный идентификатор операции")
    wallet_id: UUID = Field(..., description="ID кошелька, к которому относится операция")
    operation_type: OperationType = Field(..., description="Тип операции")
    status: OperationStatus = Field(..., description="Статус операции")
    amount: Decimal = Field(..., description="Сумма операции")
    fee: Decimal = Field(..., description="Комиссия за операцию")
    total_amount: Decimal = Field(..., description="Общая сумма (сумма + комиссия)")
    created_at: datetime = Field(..., description="Дата и время создания операции")

    model_config = ConfigDict(from_attributes=True)
