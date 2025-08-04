from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, status, Path

from api.v1.payment.schemas import SbpPaymentCreate, SbpPaymentResponse
from api.v1.payment.dependencies import PaymentServiceDep
from api.v1.auth.dependencies import UserAuthDep

router = APIRouter(tags=["Payment"])


@router.post(
    "/wallet/{wallet_id}/one-pay",
    status_code=status.HTTP_200_OK,
    response_model=SbpPaymentResponse,
)
async def create_sbp_payment(
    user: UserAuthDep,
    payment_data: SbpPaymentCreate,
    service: PaymentServiceDep,
    wallet_id: Annotated[UUID, Path(..., description="ID кошелька")],
) -> SbpPaymentResponse:
    """Создать новый SBP платеж"""
    return await service.create_sbp_payment(user.id, wallet_id, payment_data)
