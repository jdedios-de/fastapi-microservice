from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime

from sqlmodel import Field, SQLModel


class APIKeys(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    api_key: str
    expires_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    is_active: bool
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        sa_type=DateTime(timezone=True)
    )

    user_id: int = Field(default=None, foreign_key="users.id")
