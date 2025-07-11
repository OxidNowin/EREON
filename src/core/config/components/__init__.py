from core.config.components.base import BaseConfig
from core.config.components.db import DatabaseConfig
from core.config.components.redis import RedisConfig
from core.config.components.external_api import ExternalApiConfig


class ComponentsConfig(BaseConfig, DatabaseConfig, RedisConfig, ExternalApiConfig):
    pass


__all__ = ["ComponentsConfig"]
