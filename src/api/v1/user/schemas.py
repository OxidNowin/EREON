from pydantic import BaseModel, Field, EmailStr


class UserResponse(BaseModel):
    telegram_id: int
    email: EmailStr


class UserEmail(BaseModel):
    email: EmailStr = Field(..., description="Email address")


class UserChangeCode(BaseModel):
    old_code: str = Field(..., description="Old code to change", min_length=4, max_length=4, examples=["1234"])
    new_code: str = Field(..., description="New Code", min_length=4, max_length=4, examples=["1235"])



