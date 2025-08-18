from typing import AsyncIterator, Annotated

from fastapi import Depends

from api.v1.wallet.service import WalletService
from crypto_processing.client import CryptoProcessingClient
from infra.postgres.uow import PostgresUnitOfWorkDep


async def get_wallet_service(uow: PostgresUnitOfWorkDep) -> AsyncIterator[WalletService]:
    yield WalletService(
        uow=uow,
        crypto_processing_client=CryptoProcessingClient()
    )


WalletServiceDep = Annotated[WalletService, Depends(get_wallet_service)]
