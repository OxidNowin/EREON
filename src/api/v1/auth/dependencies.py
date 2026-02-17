import logging
from typing import AsyncIterator, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBase
from telegram_webapp_auth.auth import TelegramAuthenticator, generate_secret_key, WebAppUser
from telegram_webapp_auth.errors import InvalidInitDataError

from api.v1.auth.service import RegisterService, LoginService
from core.config import settings
from crypto_processing.client import CryptoProcessingClient
from infra.postgres.uow import PostgresUnitOfWorkDep
from infra.redis.dependencies import RedisDep

logger = logging.getLogger(__name__)

telegram_authentication_schema = HTTPBase(scheme="Bearer")


def get_telegram_authenticator() -> TelegramAuthenticator:
    secret_key = generate_secret_key(settings.telegram_bot_token)
    return TelegramAuthenticator(secret_key)


async def get_register_service(uow: PostgresUnitOfWorkDep, redis: RedisDep) -> AsyncIterator[RegisterService]:
    yield RegisterService(
        uow=uow,
        redis=redis,
        crypto_processing_client=CryptoProcessingClient(),
    )


async def get_login_service(uow: PostgresUnitOfWorkDep, redis: RedisDep) -> AsyncIterator[LoginService]:
    yield LoginService(
        uow=uow,
        redis=redis
    )


async def get_current_user(
    service: Annotated[RegisterService, Depends(get_register_service)],
    auth_cred: Annotated[HTTPAuthorizationCredentials, Depends(telegram_authentication_schema)],
    telegram_authenticator: Annotated[TelegramAuthenticator, Depends(get_telegram_authenticator)],
) -> WebAppUser:
    try:
        init_data = telegram_authenticator.validate(auth_cred.credentials)
    except InvalidInitDataError as e:
        # Important: do NOT log full initData (it contains user data + signature)
        preview = auth_cred.credentials[:64] + "..." if auth_cred.credentials else "<empty>"
        logger.warning(
            "Telegram initData validation failed: %s (len=%s, preview=%s)",
            str(e),
            len(auth_cred.credentials) if auth_cred.credentials else 0,
            preview,
        )
        detail = "Forbidden access."
        if getattr(settings, "DEBUG", False):
            # Helps diagnose in dev without exposing initData itself
            detail = f"Forbidden access. Invalid initData: {str(e)}"
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
    except Exception:
        logger.exception("Unexpected error during Telegram initData validation")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error.")

    if init_data.user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found in initData.")

    tg_user = init_data.user

    if not await service.exist(tg_user.id):
        referral_code = getattr(init_data, 'start_param', None)
        await service.register_user(tg_user.id, referral_code=referral_code)

    if not await service.is_login(tg_user.id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="need to log in.")

    return tg_user


LoginServiceDep = Annotated[LoginService, Depends(get_login_service)]
UserAuthDep = Annotated[WebAppUser, Depends(get_current_user)]
