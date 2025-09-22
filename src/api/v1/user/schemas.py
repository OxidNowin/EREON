from pydantic import BaseModel, Field, EmailStr


class UserEmail(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="Email адрес пользователя для верификации",
        examples=["user@example.com", "test@gmail.com"]
    )


class UserChangeCode(BaseModel):
    old_code: str = Field(
        ..., 
        description="Текущий 4-значный код входа для подтверждения",
        min_length=4, 
        max_length=4, 
        examples=["1234", "5678", "9999"]
    )
    new_code: str = Field(
        ..., 
        description="Новый 4-значный код входа",
        min_length=4, 
        max_length=4, 
        examples=["1235", "5679", "0000"]
    )

class UserSetCode(BaseModel):
    code: str = Field(
        ...,
        description="4-значный код входа",
        min_length=4,
        max_length=4,
        examples=["1234", "5678", "9999"]
    )



