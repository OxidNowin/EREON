from typing import Sequence
from uuid import UUID

from api.v1.base.service import BaseService
from api.v1.base.schemas import PaginationParams
from api.v1.operation.schemas import OperationBase, TRONSCAN_TX_URL
from infra.postgres.models import Operation


class OperationService(BaseService):
    def _to_operation_base(self, op: Operation) -> OperationBase:
        base = OperationBase.model_validate(op)
        if op.crypto_replenishment:
            return OperationBase(
                **base.model_dump(),
                tx_id=op.crypto_replenishment.tx_id,
                network="TRC20",
                explorer_url=f"{TRONSCAN_TX_URL}/{op.crypto_replenishment.tx_id}",
            )
        return base

    async def get_operations_by_wallet(
            self,
            wallet_id: UUID,
            params: PaginationParams,
    ) -> Sequence[OperationBase]:
        operations = await self.uow.operation.get_wallet_operations(
            wallet_id=wallet_id,
            limit=params.limit,
            offset=params.offset,
        )
        return [self._to_operation_base(op) for op in operations]

    async def get_operations_by_user(
            self,
            telegram_id: int,
            params: PaginationParams,
    ) -> Sequence[OperationBase]:
        operations = await self.uow.operation.get_user_operations(
            telegram_id=telegram_id,
            limit=params.limit,
            offset=params.offset,
        )
        return [self._to_operation_base(op) for op in operations]

    async def get_operation(self, operation_id: UUID) -> OperationBase | None:
        op = await self.uow.operation.get_operation(operation_id)
        if op is None:
            return None
        return self._to_operation_base(op)
