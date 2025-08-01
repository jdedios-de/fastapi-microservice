from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str
    email: str
    is_active: bool = Field(default=True)
    is_disabled: bool = Field(default=False)


class UserUpdate(BaseModel):
    is_active: bool = Field(default=False)
    email: str = None

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password_hash: str


class UserCreateRolePermission(UserBase):
    password_hash: str
    role: str
    permission: str
    permission_description: str


class User(UserBase):
    id: Optional[int] = None
    password_hash: str

    class Config:
        from_attributes = True
