from typing import AsyncIterator, Annotated

from fastapi import Depends

from api.v1.auth.service import (
    RegisterService,
    LoginService,
)
from crypto_processing.client import CryptoProcessingClient
from infra.postgres.uow import PostgresUnitOfWorkDep


async def get_register_service(uow: PostgresUnitOfWorkDep) -> AsyncIterator[RegisterService]:
    yield RegisterService(
        uow=uow,
        crypto_processing_client=CryptoProcessingClient()
    )


async def get_login_service(uow: PostgresUnitOfWorkDep) -> AsyncIterator[LoginService]:
    yield LoginService(uow=uow)


RegisterServiceDep = Annotated[RegisterService, Depends(get_register_service)]
LoginServiceDep = Annotated[LoginService, Depends(get_login_service)]
