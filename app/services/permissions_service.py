from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db import get_session
from app.dependencies import get_db
from app.models.users import Roles, Permissions
from app.schemas.permissions import PermissionBase
from sqlalchemy.exc import IntegrityError


class PermissionService:
    @staticmethod
    async def service_get_permission_by_id(permission_id: int, session: AsyncSession):
        try:
            async with session:
                statement = select(Permissions).where(Permissions.id == permission_id)
                results = await session.execute(statement)
                return results.first()
        except IntegrityError:
            await session.rollback()
            raise

    @staticmethod
    async def service_get_permission_by_name(permission_name: str, session: AsyncSession):
        try:
            async with session:
                statement = select(Permissions).where(
                    Permissions.permission_name == permission_name)
                results = await session.execute(statement)
                return results.first()
        except IntegrityError:
            await session.rollback()
            raise

    @staticmethod
    async def service_create_permission(permission: PermissionBase, session: AsyncSession) -> Permissions:
        try:
            db_permission = Permissions(
                permission_name=permission.permission_name,
                description=permission.description
            )

            async with session:
                session.add(db_permission)
                await session.commit()
                await session.refresh(db_permission)
                return db_permission
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=409,
                                detail="Permission already exists")

    @staticmethod
    async def service_delete_permission(permission_id: int, session: AsyncSession):
        async with session:
            permission = await session.get(Permissions, permission_id)
            await session.delete(permission)
            await session.commit()
            return permission

    @staticmethod
    async def service_update_permission(permission_id: int,
                                        permission: PermissionBase, session: AsyncSession) -> Permissions:
        try:
            async with session:
                db_permission = await session.get(Roles, permission_id)
            if db_permission is None:
                raise HTTPException(status_code=404,
                                    detail="Permission not found")

            user_data = permission.model_dump(exclude_unset=True)
            for key, value in user_data.items():
                setattr(db_permission, key, value)

            async with session:
                await session.add(db_permission)
                await session.commit()
                await session.refresh(db_permission)

            return db_permission
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=409,
                                detail="Permission already exists")
