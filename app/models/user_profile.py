from datetime import datetime, date
from typing import Optional
from zoneinfo import ZoneInfo

from sqlmodel import Field, SQLModel, Relationship

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