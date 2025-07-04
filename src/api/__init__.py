from fastapi import APIRouter

from api.metrics import router as metrics_router


v1_router = APIRouter(prefix="/api/v1", tags=["v1"])


__all__ = [
    "v1_router",
    "metrics_router",
]
