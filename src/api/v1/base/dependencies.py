from typing import Annotated
from fastapi import Query, Depends

from api.v1.base.schemas import PaginationParams


def pagination_params(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)


def get_telegram_id(telegram_id: int = Query(..., gt=0,  description="Telegram ID")) -> int:
    return telegram_id


TelegramIDDep = Annotated[int, Depends(get_telegram_id)]
PaginationDep = Annotated[PaginationParams, Depends(pagination_params)]
