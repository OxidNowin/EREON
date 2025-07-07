from fastapi import APIRouter, status

from api.v1.auth.schemas import UserCreate, UserLogin
from api.v1.auth.dependencies import (
    RegisterServiceDep,
    LoginServiceDep
)
from api.v1.base.dependencies import TelegramIDDep

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(telegram_id: TelegramIDDep, user: UserCreate, service: RegisterServiceDep):
    await service.register_user(telegram_id, user)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(telegram_id: TelegramIDDep, user: UserLogin, service: LoginServiceDep) -> bool:
    return await service.login_by_code(telegram_id, user)
