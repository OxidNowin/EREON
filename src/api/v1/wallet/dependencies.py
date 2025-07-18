from typing import AsyncIterator, Annotated

from fastapi import Depends

from api.v1.wallet.service import WalletService
from infra.postgres.uow import PostgresUnitOfWorkDep


async def get_wallet_service(uow: PostgresUnitOfWorkDep) -> AsyncIterator[WalletService]:
    yield WalletService(uow=uow)


WalletServiceDep = Annotated[WalletService, Depends(get_wallet_service)]
