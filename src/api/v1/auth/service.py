from uuid import uuid4

from api.v1.base.service import BaseService
from api.v1.auth.schemas import UserLogin
from infra.postgres.models import User, Referral, Wallet, WalletCurrency
from api.v1.auth.exceptions import InvalidEntryCodeError


class RegisterService(BaseService):
    USER_REDIS_SPACENAME: str = "user"
    USER_LOGIN_REDIS_SPACENAME: str = "user_login"

    USER_REDIS_EXPIRE = 3600
    USER_LOGIN_REDIS_EXPIRE = 900

    async def exist(self, telegram_id: int) -> bool:
        key = f"{self.USER_REDIS_SPACENAME}:{telegram_id}"
        if await self.redis.exists(key):
            await self.redis.set(key, "", self.USER_REDIS_EXPIRE)
            return True

        user_exist = await self.uow.user.exists(telegram_id)
        if user_exist:
            await self.redis.set(key, "", self.USER_REDIS_EXPIRE)
            return True
        return False

    async def is_login(self, telegram_id: int) -> bool:
        key = f"{self.USER_LOGIN_REDIS_SPACENAME}:{telegram_id}"
        if await self.redis.exists(key):
            await self.redis.set(key, "", self.USER_LOGIN_REDIS_EXPIRE)
            return True

        has_entry_code = await self.uow.user.has_entry_code(telegram_id)
        if not has_entry_code:
            return True

        return False

    async def register_user(self, telegram_id: int, referral_code: str | None = None) -> None:
        await self._create_user(telegram_id)
        await self._create_referral(telegram_id, referral_code)
        await self._create_wallet(telegram_id)
        await self.redis.set(f"{self.USER_REDIS_SPACENAME}:{telegram_id}", "", self.USER_REDIS_EXPIRE)

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
        
        # Отправляем уведомление рефереру о присоединении нового реферала
        if referred_by is not None:
            try:
                await self._send_notification(
                    telegram_id=referred_by,
                    notification_type="referral_join",
                    title="Новый реферал",
                    message=f"К вам присоединился новый реферал {telegram_id}",
                    referral_id=telegram_id,
                    referral_username=None
                )
            except Exception as e:
                # Логируем ошибку, но не прерываем процесс регистрации
                pass

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
    USER_LOGIN_REDIS_SPACENAME: str = "user_login"
    USER_LOGIN_REDIS_EXPIRE = 900

    async def login_by_code(self, login_data: UserLogin) -> None:
        key = f"{self.USER_LOGIN_REDIS_SPACENAME}:{login_data.telegram_id}"
        if await self.redis.exists(key):
            await self.redis.set(key, "", self.USER_LOGIN_REDIS_EXPIRE)
            return

        checked = await self.uow.user.check_user_code(
            telegram_id=login_data.telegram_id,
            entry_code=login_data.entry_code
        )
        if not checked:
            raise InvalidEntryCodeError(f"Invalid entry code for user with telegram_id {login_data.telegram_id}")
        await self.redis.set(key, "", self.USER_LOGIN_REDIS_EXPIRE)
