from pydantic import BaseModel, Field


class UserBase(BaseModel):
    entry_code: str = Field(
        ..., 
        description="4-значный код входа для аутентификации",
        min_length=4, 
        max_length=4,
        examples=["1234", "5678", "9999"]
    )


class UserLogin(UserBase):
    telegram_id: int = Field(
        ..., 
        description="Уникальный идентификатор пользователя в Telegram",
        examples=[123456789, 987654321, 555666777]
    )
