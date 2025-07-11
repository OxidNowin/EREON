from typing import AsyncIterator, Annotated

from fastapi import Depends

from api.v1.operation.service import OperationService
from infra.postgres.uow import PostgresUnitOfWorkDep


async def get_operation_service(uow: PostgresUnitOfWorkDep) -> AsyncIterator[OperationService]:
    yield OperationService(uow=uow)


OperationServiceDep = Annotated[OperationService, Depends(get_operation_service)]
