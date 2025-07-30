from datetime import datetime, timedelta, timezone

import jwt

from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import Users
from app.services.user_service import UserService
from app.utils.env import get_key

ALGORITHM = "HS256"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username: str, session: AsyncSession, cache, tracer) -> Users:
    return await UserService.get_user_by_username(username, session, cache, tracer)


async def authenticate_user(username: str, password: str, session: AsyncSession, cache, tracer) -> Users:
    user: Users = await get_user(username, session, cache, tracer)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, get_key(), algorithm=ALGORITHM)
