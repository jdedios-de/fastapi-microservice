from pydantic import EmailStr

from datetime import timezone
from sqlalchemy import DateTime
from typing import List,Optional

from datetime import datetime, date
from zoneinfo import ZoneInfo

from sqlmodel import Field, SQLModel, Relationship

class UserRoles(SQLModel, table=True):
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True)
    )
    role_id: Optional[int] = Field(default=None, foreign_key="roles.id", primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", primary_key=True)


class RolePermissions(SQLModel, table=True):
    granted_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True)
    )
    role_id: int = Field(foreign_key="roles.id", primary_key=True, nullable=False)
    permission_id: int = Field(foreign_key="permissions.id", primary_key=True, nullable=False)

class UserProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str = Field(nullable=False, index=True)
    last_name: str = Field(nullable=False)
    sex: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    birth_date: date
    bio: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(ZoneInfo("UTC"))
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(ZoneInfo("UTC")),
        sa_column_kwargs={"onupdate": lambda: datetime.now(ZoneInfo("UTC"))},
    )
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    user: Optional["Users"] = Relationship(back_populates="profile")

class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: EmailStr = Field(unique=True, index=True)
    password_hash: str
    is_active: bool = Field(default=True)
    is_disabled: bool = Field(default=False)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    roles: List["Roles"] = Relationship(back_populates="users", link_model=UserRoles)
    profile: Optional[UserProfile] = Relationship(back_populates="user")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_disabled": self.is_disabled
        }

class Roles(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role_name: str = Field(unique=True, index=True)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True)
    )
    users: List["Users"] = Relationship(back_populates="roles", link_model=UserRoles)
    permissions: List["Permissions"] = Relationship(back_populates="roles", link_model=RolePermissions)

    def to_dict(self):
        return {
            "id": self.id,
            "role_name": self.role_name
        }


class Permissions(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    permission_name: str = Field(unique=True, index=True)
    description: str
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True)
    )
    roles: List["Roles"] = Relationship(back_populates="permissions", link_model=RolePermissions)

    def to_dict(self):
        return {
            "id": self.id,
            "permission_name": self.permission_name,
            "description": self.description,
        }