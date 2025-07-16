from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.config.constants import ENV_FILE_PATH


class AlfaApiConfig(BaseSettings):
    base_url: str = Field("https://sandbox.alfabank.ru", description="Базовый URL сервиса СБП")
    client_id: str = Field("0cee0683-85ae-49f2-a63d-29f97aad1911", description="Идентификатор партнёрского сервиса")
    client_secret: str = Field(default="Qwerty1234567890Qwerty1234567890!", description="Секретный ключ партнёрского сервиса")

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding='utf-8',
        env_prefix="ALFA_",
    )
