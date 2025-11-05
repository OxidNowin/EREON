from typing import AsyncIterator, Annotated

from fastapi import Depends

from api.v1.payment.service import PaymentService
from infra.postgres.uow import PostgresUnitOfWorkDep
from infra.redis.dependencies import RedisDep
from banking.dependencies import BankClientDep


async def get_payment_service(
        uow: PostgresUnitOfWorkDep,
        bank_client: BankClientDep,
        redis: RedisDep
) -> AsyncIterator[PaymentService]:
    yield PaymentService(
        uow=uow,
        bank_client=bank_client,
        redis=redis
    )


PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
