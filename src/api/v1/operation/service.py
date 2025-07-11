from typing import Sequence
from uuid import UUID

from api.v1.base.service import BaseService
from api.v1.base.schemas import PaginationParams
from infra.postgres.models import Operation


class OperationService(BaseService):
    async def get_operations_by_wallet(
            self,
            wallet_id: UUID,
            params: PaginationParams,
    ) -> Sequence[Operation]:
        return await self.uow.operation.get_wallet_operations(
            wallet_id=wallet_id,
            limit=params.limit,
            offset=params.offset,
        )

    async def get_operations_by_user(
            self,
            telegram_id: int,
            params: PaginationParams,
    ) -> Sequence[Operation]:
        return await self.uow.operation.get_user_operations(
            telegram_id=telegram_id,
            limit=params.limit,
            offset=params.offset,
        )

    async def get_operation(self, operation_id: UUID) -> Operation:
        return await self.uow.operation.get_operation(operation_id)
