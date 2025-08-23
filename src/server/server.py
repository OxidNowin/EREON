from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from core.config import settings
from core.logging_config import setup_logging
from core.error_handler import register_exception_handlers


def _init_router(_app: FastAPI) -> None:
    from api import metrics_router, v1_router

    _app.include_router(v1_router)
    _app.include_router(metrics_router)


def _init_prometheus(_app: FastAPI) -> None:
    instrumentator = Instrumentator(
        excluded_handlers=["/metrics", "/docs", "/redoc", "/openapi.json", "/healthcheck"]
    )
    instrumentator.instrument(_app).expose(_app)


def _init_middleware(_app: FastAPI) -> None:
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging(
        log_to_file=False if settings.DEBUG else True,
    )
    yield


def create_app() -> FastAPI:
    description = (
        "**API for EREON**\n\n"
        "**Инструкция по авторизации:**\n\n"
        "1. Перейдите в [ТГ-бота](https://t.me/ereon_test_bot) и откройте в нем TMA\n"
        "2. Скопируйте TelegramInitData -- это будет ваш Bearer Token\n"
        "3. Чтобы протестировать в свагере: нажмите кнопку **Authorize** и вставьте туда полученную строку"
    )
    _app = FastAPI(
        title="EREON",
        description=description,
        version="1.0.0",
        lifespan=lifespan,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
    )
    _init_router(_app)
    _init_middleware(_app)
    _init_prometheus(_app)
    register_exception_handlers(_app)
    return _app


app = create_app()
