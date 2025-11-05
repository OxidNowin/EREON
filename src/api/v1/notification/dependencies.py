from typing import AsyncIterator, Annotated

from fastapi import Depends

from api.v1.notification.service import NotificationService
from infra.postgres.uow import PostgresUnitOfWorkDep
from infra.redis.dependencies import RedisDep


async def get_notification_service(
    uow: PostgresUnitOfWorkDep,
    redis: RedisDep
) -> AsyncIterator[NotificationService]:
    service = NotificationService(uow=uow, redis=redis)
    yield service


NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]

