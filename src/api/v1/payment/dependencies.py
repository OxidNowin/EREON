from typing import AsyncIterator, Annotated

from fastapi import Depends

from api.v1.payment.service import PaymentService
from infra.postgres.uow import PostgresUnitOfWorkDep
from banking.dependencies import BankClientDep


async def get_payment_service(
        uow: PostgresUnitOfWorkDep,
        bank_client: BankClientDep
) -> AsyncIterator[PaymentService]:
    yield PaymentService(
        uow=uow,
        bank_client=bank_client
    )


PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]
