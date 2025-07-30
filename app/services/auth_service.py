from datetime import datetime
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.api_keys import APIKeys
from app.models.users import Users
from app.schemas.apikeys import ApiKeysBase, ApiKeysVerify
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.services.user_service import UserService


class AuthenticateService:
    @staticmethod
    async def service_create_api_key(api_key: ApiKeysBase, session: AsyncSession, cache, tracer) -> APIKeys:
        try:

            user = await UserService.get_user_by_id(api_key.user_id, session, cache, tracer)

            if user is None:
                raise HTTPException(status_code=404,
                                    detail="Username does not exists")
            db_api_key = APIKeys(
                api_key=api_key.api_key,
                user_id=api_key.user_id,
                expires_at=api_key.expires_at,
                is_active=api_key.is_active
            )

            async with session:
                session.add(db_api_key)
                await session.commit()
                await session.refresh(db_api_key)
                return db_api_key
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=409,
                                detail="Error in generating api key")

    @staticmethod
    async def is_api_key_expired_set_inactive(api_key: str, db=Depends(get_db)) -> bool:
        try:
            with db as session:
                statement = select(APIKeys).where(
                    APIKeys.api_key == api_key).where(
                    APIKeys.is_active == True).where(
                    APIKeys.expires_at < datetime.now())

                results = await session.exec(statement).first()

                if results:
                    key = await session.get(APIKeys, results.id)
                    key.is_active = False
                    await session.add(key)
                    await session.commit()
                    await session.refresh(key)
                    return True
                return False
        except IntegrityError:
            await session.rollback()
            raise

    @staticmethod
    async def is_api_key_active(api_key: ApiKeysVerify, db=Depends(get_db)):
        try:
            with db as session:
                statement = select(APIKeys).join(Users).where(
                    APIKeys.api_key == api_key.api_key).where(
                    APIKeys.is_active == True).where(
                    APIKeys.expires_at > datetime.now()).where(
                    Users.is_active == True)

                results = await session.exec(statement).first()

                if not results:
                    return False
                return True
        except IntegrityError:
            await session.rollback()
            raise