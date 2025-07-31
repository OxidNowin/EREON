from typing import Annotated, AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infra.postgres.pg import get_db
from infra.postgres.storage.user import UserStorage
from infra.postgres.storage.referral import ReferralStorage
from infra.postgres.storage.wallet import WalletStorage
from infra.postgres.storage.operation import OperationStorage
from infra.postgres.storage.cryptocurrency_replenishment import CryptocurrencyReplenishmentStorage
from infra.postgres.storage.sbp_payment import SbpPaymentStorage


class PostgresUnitOfWork:
    """
    A single entry point for working with storages.
    Manages access to data storages using the provided database session.
    """
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user = UserStorage(db)
        self.referral = ReferralStorage(db)
        self.wallet = WalletStorage(db)
        self.operation = OperationStorage(db)
        self.cryptocurrency_replenishment = CryptocurrencyReplenishmentStorage(db)
        self.sbp_payment = SbpPaymentStorage(db)


async def get_uow() -> AsyncIterator[PostgresUnitOfWork]:
    async with get_db() as db:
        yield PostgresUnitOfWork(db)


PostgresUnitOfWorkDep = Annotated[PostgresUnitOfWork, Depends(get_uow)]
