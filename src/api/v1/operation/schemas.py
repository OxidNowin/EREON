from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from api.v1.base.schemas import DisplayDecimal
from infra.postgres.models import OperationType, OperationStatus


class OperationBase(BaseModel):
    operation_id: UUID = Field(..., description="Уникальный идентификатор операции")
    wallet_id: UUID = Field(..., description="ID кошелька, к которому относится операция")
    operation_type: OperationType = Field(..., description="Тип операции")
    status: OperationStatus = Field(..., description="Статус операции")
    amount: DisplayDecimal = Field(..., description="Сумма операции")
    fee: DisplayDecimal = Field(..., description="Комиссия за операцию")
    total_amount: DisplayDecimal = Field(..., description="Общая сумма (сумма + комиссия)")
    created_at: datetime = Field(..., description="Дата и время создания операции")

    model_config = ConfigDict(from_attributes=True)
