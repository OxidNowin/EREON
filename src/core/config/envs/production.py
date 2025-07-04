from pydantic_settings import BaseSettings, SettingsConfigDict

from core.config.constants import ENV_FILE_PATH


class ProductionConfig(BaseSettings):
    DEBUG: bool = False
    reload: bool = False
    workers: int = 8

    docs_url: str | None = None
    redoc_url: str | None = None

    # CORS settings
    cors_origins: list[str] = []
    cors_allow_credentials: bool = False
    cors_allow_methods: list[str] = []
    cors_allow_headers: list[str] = []

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding='utf-8',
    )
