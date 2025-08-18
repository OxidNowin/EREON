from uuid import UUID

from fastapi import APIRouter

from api.v1.operation.schemas import OperationBase
from api.v1.operation.dependencies import OperationServiceDep
from api.v1.base.dependencies import PaginationDep
from api.v1.auth.dependencies import UserAuthDep
from infra.postgres.models import Operation

router = APIRouter(tags=["Operation"])


@router.get("/user/operations", response_model=list[OperationBase])
async def get_user_operations_handler(
    user: UserAuthDep,
    params: PaginationDep,
    service: OperationServiceDep,
):
    return await service.get_operations_by_user(
        telegram_id=user.id,
        params=params
    )


@router.get("/wallet/{wallet_id}/operations", response_model=list[OperationBase])
async def get_wallet_operations_handler(
    user: UserAuthDep,
    wallet_id: UUID,
    params: PaginationDep,
    service: OperationServiceDep,
):
    return await service.get_operations_by_wallet(
        wallet_id=wallet_id,
        params=params
    )


@router.get("/operations/{operation_id}", response_model=OperationBase)
async def get_operation_handler(
    user: UserAuthDep,
    operation_id: UUID,
    service: OperationServiceDep
) -> Operation:
    return await service.get_operation(operation_id)
