from fastapi import APIRouter, status

from api.v1.auth.schemas import UserCreate, UserLogin
from api.v1.auth.dependencies import (
    RegisterServiceDep,
    LoginServiceDep
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, service: RegisterServiceDep):
    await service.register_user(user)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(user: UserLogin, service: LoginServiceDep) -> bool:
    return await service.login_by_code(user)
