from fastapi import APIRouter, status

from api.v1.webhook.dependencies import WebhookServiceDep
from api.v1.webhook.schemas import CryptocurrencyReplenishmentCreate

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("", status_code=status.HTTP_200_OK)
async def get_webhook(data: CryptocurrencyReplenishmentCreate, webhook_service: WebhookServiceDep):
    if data.type == "refill":
        await webhook_service.add_balance(data)
    return {"status": "ok"}
