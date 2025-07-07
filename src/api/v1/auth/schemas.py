from pydantic import BaseModel, Field


class UserBase(BaseModel):
    entry_code: str = Field(..., description="Entry code", min_length=4, max_length=4)


class UserCreate(UserBase):
    referral_code: str | None = Field(None, description="Referral code")


class UserLogin(UserBase):
    ...
