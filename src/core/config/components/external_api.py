from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.config.constants import ENV_FILE_PATH


class ExternalApiConfig(BaseSettings):
    crypto_processing_base_url: str = Field(default="", description="Базовый URL сервиса по крипто-процессингу")
    crypto_processing_token: str = Field(default="", description="Токен для аутентификации на сервисе крипто-процессинга")

    sbp_base_url: str = Field(default="", description="Базовый URL сервиса СБП")
    sbp_token: str = Field(default="", description="Токен для аутентификации на сервисе СБП")

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding='utf-8',
    )
