from fastapi import APIRouter, Depends

from api.metrics import router as metrics_router
from api.v1 import auth_router, user_router, wallet_router, webhook_router, operation_router
from api.v1.base.dependencies import get_telegram_id


v1_router = APIRouter(prefix="/api/v1", tags=["v1"])
v1_router.include_router(auth_router, dependencies=[Depends(get_telegram_id)])
v1_router.include_router(user_router, dependencies=[Depends(get_telegram_id)])
v1_router.include_router(wallet_router, dependencies=[Depends(get_telegram_id)])
v1_router.include_router(operation_router, dependencies=[Depends(get_telegram_id)])
v1_router.include_router(webhook_router)


__all__ = [
    "v1_router",
    "metrics_router",
]
