from fastapi import APIRouter, status

from api.v1.user.schemas import UserChangeCode
from api.v1.user.dependencies import UserServiceDep
from api.v1.base.dependencies import TelegramIDDep

router = APIRouter(prefix="/user", tags=["User"])


@router.patch("/code", status_code=status.HTTP_200_OK)
async def change_entry_code(
    telegram_id: TelegramIDDep, 
    codes: UserChangeCode, 
    service: UserServiceDep
) -> bool:
    return await service.change_entry_code(telegram_id, codes)
