from dataclasses import dataclass

from crypto_processing.client import CryptoProcessingClient
from infra.postgres.uow import PostgresUnitOfWork


@dataclass(slots=True)
class BaseService:
    uow: PostgresUnitOfWork
    crypto_processing_client: CryptoProcessingClient | None = None
