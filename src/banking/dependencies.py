from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends

from infra.redis.dependencies import get_redis
from infra.redis.redis_api import RedisAPI
from banking.abstractions import ITokenService, IBankPaymentClient
from banking.providers.alfa import AlfaClient, AlfaTokenService, AlfaScope


def get_alfa_token_service(
    redis: RedisAPI = Depends(get_redis),
) -> ITokenService[AlfaScope]:
    """Получить сервис управления токенами Alfa Bank"""
    return AlfaTokenService(redis=redis)


@asynccontextmanager
async def get_alfa_client(
    token_service: ITokenService[AlfaScope] = Depends(get_alfa_token_service),
) -> AsyncIterator[IBankPaymentClient]:
    """Получить клиент для работы с Alfa Bank API с автоматическим закрытием сессии"""
    client = AlfaClient(token_service=token_service)
    try:
        yield client
    finally:
        await client.close()


# Общие алиасы (по умолчанию используем Alfa Bank)
@asynccontextmanager
async def get_default_bank_client(
    alfa_client: IBankPaymentClient = Depends(get_alfa_client),
) -> AsyncIterator[IBankPaymentClient]:
    """Получить клиент банка по умолчанию (Alfa Bank) с автоматическим закрытием сессии"""
    yield alfa_client