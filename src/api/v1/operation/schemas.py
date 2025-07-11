from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from infra.postgres.models import OperationType, OperationStatus


class OperationBase(BaseModel):
    operation_id: UUID
    wallet_id: UUID
    operation_type: OperationType
    status: OperationStatus
    amount: Decimal
    fee: Decimal
    total_amount: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
