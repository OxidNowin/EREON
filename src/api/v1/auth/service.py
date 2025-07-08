from uuid import uuid4

from api.v1.base.service import BaseService
from api.v1.auth.schemas import UserCreate, UserLogin
from infra.postgres.models import User, Referral, Wallet, WalletCurrency


class RegisterService(BaseService):
    async def register_user(self, telegram_id: int, user: UserCreate) -> None:
        await self.create_user(telegram_id, user)
        await self.create_referral(telegram_id, user)
        await self.create_wallet(telegram_id)

    async def create_user(self, telegram_id: int, user: UserCreate) -> User:
        return await self.uow.user.add(
            User(
                telegram_id=telegram_id,
                entry_code=user.entry_code,
            )
        )

    async def create_referral(self, telegram_id: int, user: UserCreate) -> Referral:
        referred_by = None
        if user.referral_code is not None:
            referred_by = await self.uow.referral.get_id_by_referral_code(user.referral_code)

        active = False
        if referred_by is not None:
            active = True

        return await self.uow.referral.add(
            Referral(
                telegram_id=telegram_id,
                referred_by=referred_by,
                code=self.generate_referral_code(),
                active=active,
            )
        )

    async def create_wallet(self, telegram_id: int) -> Wallet:
        return await self.uow.wallet.add(
            Wallet(
                telegram_id=telegram_id,
                currency=WalletCurrency.USDT,
                addresses=['TLcsfBDnvUTxF6ZiJZQANyKLyYLY9FbPKE'],
            )
        )

    @staticmethod
    def generate_referral_code() -> str:
        return uuid4().hex


class LoginService(BaseService):
    async def login_by_code(self, telegram_id: int, user: UserLogin) -> bool:
        return await self.uow.user.check_user_code(telegram_id=telegram_id, entry_code=user.entry_code)
