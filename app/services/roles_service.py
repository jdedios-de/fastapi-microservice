from fastapi import HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.users import Roles
from app.schemas.roles import RoleBase



class RoleService:
    @staticmethod
    async def service_get_role_by_id(role_id: int, session: AsyncSession):
        async with session:
            statement = select(Roles).where(Roles.id == role_id)
            results = await session.execute(statement)
            return results.first()

    @staticmethod
    async def service_get_role_by_name(role_name: str, session: AsyncSession):
        async with session:
            statement = select(Roles).where(Roles.role_name == role_name)
            results = await session.execute(statement)
            return results.first()

    @staticmethod
    async def service_create_role(role: RoleBase, session: AsyncSession) -> Roles:
        try:
            db_roles = Roles(
                role_name=role.role_name,
            )

            async with session:
                session.add(db_roles)
                await session.commit()
                await session.refresh(db_roles)
                return db_roles

        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=409,
                                detail="Role already exists")

    @staticmethod
    async def service_delete_role(role_id: int, session: AsyncSession):
        async with session:
            role = await session.get(Roles, role_id)
            await session.delete(role)
            await session.commit()
            return role

    @staticmethod
    async def service_update_role(role_id: int, role: RoleBase, session: AsyncSession) -> Roles:
        try:
            async with session:
                db_role = await session.get(Roles, role_id)
            if db_role is None:
                raise HTTPException(status_code=404, detail="Role not found")

            user_data = role.model_dump(exclude_unset=True)
            for key, value in user_data.items():
                setattr(db_role, key, value)

            async with session:
                session.add(db_role)
                await session.commit()
                await session.refresh(db_role)

            return db_role
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=409,
                                detail="Role already exists")
