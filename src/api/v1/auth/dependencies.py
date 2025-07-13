from typing import AsyncIterator, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBase
from telegram_webapp_auth.auth import TelegramAuthenticator, generate_secret_key, WebAppUser
from telegram_webapp_auth.errors import InvalidInitDataError

from api.v1.auth.service import RegisterService, LoginService
from core.config import settings
from crypto_processing.client import CryptoProcessingClient
from infra.postgres.uow import PostgresUnitOfWorkDep

telegram_authentication_schema = HTTPBase(scheme="Bearer")


def get_telegram_authenticator() -> TelegramAuthenticator:
    secret_key = generate_secret_key(settings.telegram_bot_token)
    return TelegramAuthenticator(secret_key)


async def get_register_service(uow: PostgresUnitOfWorkDep) -> AsyncIterator[RegisterService]:
    yield RegisterService(
        uow=uow,
        crypto_processing_client=CryptoProcessingClient()
    )


async def get_login_service(uow: PostgresUnitOfWorkDep) -> AsyncIterator[LoginService]:
    yield LoginService(uow=uow)


async def get_current_user(
    service: Annotated[RegisterService, Depends(get_register_service)],
    auth_cred: HTTPAuthorizationCredentials = Depends(telegram_authentication_schema),
    telegram_authenticator: TelegramAuthenticator = Depends(get_telegram_authenticator),
) -> WebAppUser:
    try:
        init_data = telegram_authenticator.validate(auth_cred.credentials)
    except InvalidInitDataError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden access.")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error.")

    if init_data.user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found in initData.")
    tg_user = init_data.user

    # TODO сделать кэширование
    if not await service.exist(tg_user.id):
        # TODO выяснить как передаются аргументы и подставить реферальный код при регистрации
        await service.register_user(tg_user.id)
    return tg_user


RegisterServiceDep = Annotated[RegisterService, Depends(get_register_service)]
LoginServiceDep = Annotated[LoginService, Depends(get_login_service)]
UserAuthDep = Annotated[WebAppUser, Depends(get_current_user)]
