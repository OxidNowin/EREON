from dataclasses import dataclass

from infra.postgres.uow import PostgresUnitOfWork


@dataclass(slots=True)
class BaseService:
    uow: PostgresUnitOfWork 