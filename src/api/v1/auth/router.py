from fastapi import APIRouter, status

from api.v1.auth.schemas import UserLogin
from api.v1.auth.dependencies import LoginServiceDep

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
async def login_user(data: UserLogin, service: LoginServiceDep):
    await service.login_by_code(data)
