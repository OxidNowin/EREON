from fastapi import APIRouter, status

from api.v1.user.schemas import UserChangeCode
from api.v1.user.dependencies import UserServiceDep
from api.v1.auth.dependencies import UserAuthDep

router = APIRouter(prefix="/user", tags=["User"])


@router.patch("/entry_code", status_code=status.HTTP_200_OK)
async def change_entry_code(
    user: UserAuthDep,
    codes: UserChangeCode, 
    service: UserServiceDep
):
    await service.change_entry_code(user.id, codes)
