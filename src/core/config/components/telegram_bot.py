from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.config.constants import ENV_FILE_PATH


class TelegramBotConfig(BaseSettings):
    telegram_bot_token: str = Field(default="", description="Токен бота телеграм, через которого запускается MiniApp")

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding='utf-8',
    )
