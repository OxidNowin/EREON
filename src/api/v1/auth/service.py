from uuid import uuid4

from api.v1.base.service import BaseService
from api.v1.auth.schemas import UserLogin
from infra.postgres.models import User, Referral, Wallet, WalletCurrency


class RegisterService(BaseService):
    async def exist(self, telegram_id: int) -> bool:
        return await self.uow.user.exists(telegram_id)

    async def register_user(self, telegram_id: int, referral_code: str | None = None) -> None:
        await self._create_user(telegram_id)
        await self._create_referral(telegram_id, referral_code)
        await self._create_wallet(telegram_id)

    async def _create_user(self, telegram_id: int):
        await self.uow.user.add(User(telegram_id=telegram_id))

    async def _create_referral(self, telegram_id: int, referral_code: str | None) -> None:
        referred_by = None
        if referral_code is not None:
            referred_by = await self.uow.referral.get_id_by_referral_code(referral_code)

        active = False
        if referred_by is not None:
            active = True

        await self.uow.referral.add(
            Referral(
                telegram_id=telegram_id,
                referred_by=referred_by,
                code=self.__generate_referral_code(),
                active=active,
            )
        )

    async def _create_wallet(self, telegram_id: int) -> None:
        async with self.crypto_processing_client as client:
            address = await client.register_client()

        await self.uow.wallet.add(
            Wallet(
                telegram_id=telegram_id,
                currency=WalletCurrency.USDT,
                addresses=[address.trxAddress],
            )
        )

    @staticmethod
    def __generate_referral_code() -> str:
        return uuid4().hex


class LoginService(BaseService):
    async def login_by_code(self, telegram_id: int, login_data: UserLogin) -> None:
        if not await self.uow.user.check_user_code(telegram_id=telegram_id, entry_code=login_data.entry_code):
            raise
