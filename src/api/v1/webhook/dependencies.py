from typing import AsyncIterator, Annotated

from fastapi import Depends

from api.v1.webhook.service import WebhookService
from infra.postgres.uow import PostgresUnitOfWorkDep


async def get_webhook_service(uow: PostgresUnitOfWorkDep) -> AsyncIterator[WebhookService]:
    yield WebhookService(uow=uow)


WebhookServiceDep = Annotated[WebhookService, Depends(get_webhook_service)]
