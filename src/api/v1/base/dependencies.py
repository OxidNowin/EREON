from typing import Annotated
from fastapi import Query, Depends


def get_telegram_id(telegram_id: int = Query(..., gt=0,  description="Telegram ID")) -> int:
    return telegram_id


TelegramIDDep = Annotated[int, Depends(get_telegram_id)]
