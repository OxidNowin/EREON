from typing import AsyncIterator, Annotated

from fastapi import Depends

from api.v1.referral.service import ReferralService
from infra.postgres.uow import PostgresUnitOfWorkDep


async def get_referral_service(uow: PostgresUnitOfWorkDep) -> AsyncIterator[ReferralService]:
    yield ReferralService(uow=uow)


ReferralServiceDep = Annotated[ReferralService, Depends(get_referral_service)]
