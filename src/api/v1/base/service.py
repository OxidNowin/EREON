from dataclasses import dataclass

from crypto_processing.client import CryptoProcessingClient
from infra.postgres.uow import PostgresUnitOfWork
from infra.redis.redis_api import RedisAPI


@dataclass(slots=True)
class BaseService:
    uow: PostgresUnitOfWork
    crypto_processing_client: CryptoProcessingClient | None = None
    redis: RedisAPI | None = None
