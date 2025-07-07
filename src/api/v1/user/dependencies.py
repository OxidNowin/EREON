from typing import AsyncIterator, Annotated

from fastapi import Depends

from api.v1.user.service import UserService
from infra.postgres.uow import PostgresUnitOfWorkDep


async def get_user_service(uow: PostgresUnitOfWorkDep) -> AsyncIterator[UserService]:
    yield UserService(uow=uow)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
