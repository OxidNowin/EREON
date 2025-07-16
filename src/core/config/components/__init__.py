from core.config.components.base import BaseConfig
from core.config.components.db import DatabaseConfig
from core.config.components.redis import RedisConfig
from core.config.components.external_api import ExternalApiConfig
from core.config.components.telegram_bot import TelegramBotConfig
from core.config.components.alfa import AlfaApiConfig


class ComponentsConfig(
    BaseConfig,
    DatabaseConfig,
    RedisConfig,
    ExternalApiConfig,
    TelegramBotConfig,
    AlfaApiConfig,
):
    pass


__all__ = ["ComponentsConfig"]
