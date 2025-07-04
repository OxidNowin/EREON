from core.config.components.base import BaseConfig
from core.config.components.db import DatabaseConfig
from core.config.components.redis import RedisConfig


class ComponentsConfig(BaseConfig, DatabaseConfig, RedisConfig):
    pass


__all__ = ["ComponentsConfig"]
