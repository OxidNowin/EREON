from pydantic import BaseModel, Field


class UserBase(BaseModel):
    entry_code: str = Field(..., description="Entry code", min_length=4, max_length=4)


class UserLogin(UserBase):
    ...
