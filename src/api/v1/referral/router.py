from fastapi import APIRouter, status

from api.v1.referral.schemas import (
    ReferralTypeSet, 
    ReferralInfo, 
    ReferralOperationsResponse
)
from api.v1.referral.dependencies import ReferralServiceDep
from api.v1.auth.dependencies import UserAuthDep
from api.v1.base.dependencies import PaginationDep

router = APIRouter(prefix="/referral", tags=["Referral"])


@router.patch("/type", status_code=status.HTTP_202_ACCEPTED)
async def set_referral_type(
    user: UserAuthDep,
    referral_type_data: ReferralTypeSet,
    service: ReferralServiceDep
):
    """Установить тип реферальной программы. Можно установить только один раз."""
    await service.set_referral_type(user.id, referral_type_data.referral_type)


@router.get("", status_code=status.HTTP_200_OK, response_model=ReferralInfo)
async def get_referral_info(
    user: UserAuthDep,
    service: ReferralServiceDep
):
    """Получить полную информацию о реферале"""
    return await service.get_referral_info(user.id)


@router.get("/operations", status_code=status.HTTP_200_OK, response_model=ReferralOperationsResponse)
async def get_referral_operations(
    user: UserAuthDep,
    service: ReferralServiceDep,
    pagination: PaginationDep
):
    """Получить операции реферала с пагинацией"""
    return await service.get_user_referral_operations(
        user.id, 
        limit=pagination.limit, 
        offset=pagination.offset
    )
