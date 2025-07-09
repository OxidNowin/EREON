from fastapi import APIRouter, status

from api.v1.webhook.dependencies import WebhookServiceDep
from api.v1.webhook.schemas import CryptocurrencyReplenishmentCreate

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
async def get_webhook(data: CryptocurrencyReplenishmentCreate, webhook_service: WebhookServiceDep):
    return await webhook_service.add_balance(data)
