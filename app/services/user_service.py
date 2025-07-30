import json

from opentelemetry.trace import Status, StatusCode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.schemas.user_profile import UserProfileBase
from app.schemas.user_roles import UserRole
from app.dependencies import get_db
from app.models.users import Roles, Permissions, RolePermissions, UserRoles, Users
from app.models.user_profile import UserProfile
from app.schemas.role_permission import RolePermission
from app.schemas.user import UserCreate, UserUpdate, UserCreateRolePermission
from fastapi import Depends, HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    @staticmethod
    async def get_user_by_id(user_id: int, session: AsyncSession, cache, tracer):
        with tracer.start_as_current_span(f"db-query-get_user_by_id-{user_id}") as span:
            try:
                cache_key = f"users:get_user_by_id:{user_id}"

                # Check cache first
                cached = await cache.get(cache_key)
                if cached:
                    return json.loads(cached)

                statement = select(Users).where(Users.id == user_id)
                result = await session.execute(statement)
                user = result.scalar_one_or_none()

                if user is None:
                    return None

                user_dict = user.to_dict()
                await cache.set(cache_key, json.dumps(user_dict), expire=60)

                span.set_attribute("user.id", user.id)
                span.set_attribute("user.username", user.username)
                span.set_attribute("fetched.user.success", True)
                span.add_event("fetched.user.successful", attributes={"status": True})

                return user
            except SQLAlchemyError as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    @staticmethod
    async def get_user_by_username(username: str, session: AsyncSession, cache, tracer) -> Users:
        with tracer.start_as_current_span("db-query-user") as root_span:
            root_span.set_attribute("username", username)
        try:
            cache_key = f"users:get_user_by_id:{username}"

            # Check cache first
            cached = await cache.get(cache_key)
            if cached:
                return json.loads(cached)

            # Trace the database query
            with tracer.start_as_current_span(f"db-query-get_user_by_username-{username}") as database_span:
                result = await session.execute(select(Users).where(Users.username == username))
                user = result.scalar_one_or_none()

                if user is None:
                    return None

                user_dict = user.to_dict()
                await cache.set(cache_key, json.dumps(user_dict), expire=60)

                database_span.set_attribute("user.id", user.id)
                database_span.set_attribute("fetched.user.success", True)
                database_span.add_event("fetched.user.successful", attributes={"status": True})

                return user
        except SQLAlchemyError as e:
            root_span.record_exception(e)
            root_span.set_status(Status(StatusCode.ERROR, str(e)))
            raise
        except Exception as e:
            root_span.record_exception(e)
            root_span.set_status(Status(StatusCode.ERROR, str(e)))
            raise

    @staticmethod
    async def service_delete_user(user_id: int, db=Depends(get_db)):
        try:
            with db as session:
                user = await session.get(Users, user_id)
                await session.delete(user)
                await session.commit()
                return user
        except IntegrityError:
            await session.rollback()
            raise

    @staticmethod
    async def service_create_user(user_create: UserCreate, session: AsyncSession, tracer) -> Users:
        with tracer.start_as_current_span(f"db-query-service_create_user-{user_create.username}") as create_user_span:
            try:
                hashed_password = pwd_context.hash(
                    user_create.password_hash)

                db_user = Users(
                    username=user_create.username,
                    email=user_create.email,
                    password_hash=hashed_password,
                    is_active=user_create.is_active,
                    is_disabled=user_create.is_disabled,
                )

                async with session:
                    session.add(db_user)
                    await session.commit()
                    await session.refresh(db_user)

                create_user_span.set_attribute("user.id", db_user.id)
                create_user_span.set_attribute("user.username", db_user.username)
                create_user_span.set_attribute("user.email", db_user.email)
                create_user_span.set_attribute("created.user.success", True)
                create_user_span.add_event("created.user.successful", attributes={"status": True})

                # publish event
                from app.events.rabbitmq import RabbitMQClient
                await RabbitMQClient.publish("user.created",
                                             json.dumps({"id": db_user.id, "username": db_user.username}).encode())

                return db_user

            except SQLAlchemyError as e:
                await session.rollback()
                create_user_span.record_exception(e)
                create_user_span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
            except ValueError as e:
                await session.rollback()
                create_user_span.record_exception(e)
                create_user_span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
            except Exception as e:
                await session.rollback()
                create_user_span.record_exception(e)
                create_user_span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

    @staticmethod
    async def service_create_user_with_role_permission(user_create: UserCreateRolePermission,
                                                       session: AsyncSession) -> Users:
        try:
            hashed_password = pwd_context.hash(user_create.password_hash)

            permission = Permissions(
                permission_name=user_create.permission,
                descriptions=user_create.permission_description
            )

            role = Roles(role_name=user_create.role,
                         permissions=[permission])

            db_user = Users(
                username=user_create.username,
                email=user_create.email,
                password_hash=hashed_password,
                is_active=user_create.is_active,
                is_disabled=user_create.is_disabled,
                roles=[role]
            )

            async with session:
                session.add(db_user)
                await session.commit()
                await session.refresh(db_user)
                return db_user
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=409,
                                detail="Username or email already exists")

    @staticmethod
    async def service_update_user(user_id: int, user: UserUpdate, session: AsyncSession) -> Users:
        try:
            async with session:
                db_user = session.get(Users, user_id)
            if db_user is None:
                raise HTTPException(status_code=404, detail="User not found")

            user_data = user.model_dump(exclude_unset=True)
            for key, value in user_data.items():
                setattr(db_user, key, value)

            async with session:
                session.add(db_user)
                await session.commit()
                await session.refresh(db_user)

            return db_user
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=409,
                                detail="Username or email already exists")

    @staticmethod
    async def service_create_user_profile(self, user_create_profile: UserProfileBase, session: AsyncSession, cache,
                                          tracer):
        user = self.get_user_by_id(user_create_profile.user_id, session, cache, tracer)

        if user is None:
            raise HTTPException(status_code=404,
                                detail="Username does not exists")

        db_user_profile = UserProfile(
            first_name=user_create_profile.first_name,
            last_name=user_create_profile.last_name,
            sex=user_create_profile.sex,
            phone_number=user_create_profile.phone_number,
            address=user_create_profile.address,
            birth_date=user_create_profile.birth_date,
            bio=user_create_profile.bio,
            user_id=user.id
        )

        try:
            async with session:
                session.add(db_user_profile)
                await session.commit()
                await session.refresh(db_user_profile)
                return db_user_profile
        except IntegrityError:
            await session.rollback()
            raise

    @staticmethod
    async def service_assign_permission(role_permission: RolePermission,
                                        session: AsyncSession) -> RolePermissions | None:
        try:
            async with session:
                permission = await session.get(Permissions,
                                               role_permission.permission_id)
                role = await session.get(Roles, role_permission.role_id)

                if not permission or not role:
                    raise HTTPException(status_code=404,
                                        detail="Permission or Role not found")

            role_permission = RolePermissions(
                role_id=role_permission.role_id,
                permission_id=role_permission.permission_id
            )

            async with session:
                session.add(role_permission)
                await session.commit()
                await session.refresh(role_permission)
                return role_permission
        except IntegrityError:
            await session.rollback()
            raise

    @staticmethod
    async def service_assign_role(user_roles: UserRole, session: AsyncSession) -> UserRoles | None:
        try:
            async with session:
                user = await session.get(Users, user_roles.user_id)
                role = await session.get(Roles, user_roles.role_id)

                if not user or not role:
                    raise HTTPException(status_code=404,
                                        detail="User or Role not found")

            user_roles = UserRoles(
                role_id=user_roles.role_id,
                user_id=user_roles.user_id
            )

            async with session:
                session.add(user_roles)
                await session.commit()
                await session.refresh(user_roles)
                return user_roles
        except IntegrityError:
            await session.rollback()
            raise

    @staticmethod
    async def get_user_role(user_id: int, session: AsyncSession, cache, tracer):
        try:
            cache_key = f"roles:byuserid:{user_id}"

            # Check cache first
            cached = await cache.get(cache_key)
            if cached:
                return json.loads(cached)

            # Trace the database query
            with tracer.start_as_current_span(f"db-query-get_user_role-{user_id}"):
                statement = select(Roles).join(UserRoles).where(Roles.id == user_id).where(UserRoles.user_id == user_id)
                result = await session.execute(statement)
                role = result.scalar_one_or_none()

                if role is None:
                    return None

                role_dict = role.to_dict()
                await cache.set(cache_key, json.dumps(role_dict), expire=60)
                return role
        except IntegrityError:
            raise
        except Exception:
            raise

    @staticmethod
    async def get_role_permission(role_name: str, session: AsyncSession, cache, tracer):
        try:

            cache_key = f"role_permissions:get_role_permission:{role_name}"

            # Check cache first
            cached = await cache.get(cache_key)
            if cached:
                return json.loads(cached)

            # Trace the database query
            with tracer.start_as_current_span(f"db-query-get_role_permission-{role_name}"):
                statement = (
                    select(Permissions)
                    .join(RolePermissions, RolePermissions.permission_id == Permissions.id)
                    .join(Roles, Roles.id == RolePermissions.role_id)
                    .where(Roles.role_name == role_name)
                )

                result = await session.execute(statement)
                permissions = result.scalars().all()

                if not permissions:
                    return None

                # Assuming you have a Role object from a prior query or context
                # If you need to fetch the Role, add a query for it
                statement_role = select(Roles).where(Roles.role_name == role_name)
                result_role = await session.execute(statement_role)
                role = result_role.scalars().first()

                if not role:
                    return None

                role_dict = {
                    "role_name": role.role_name,
                    "permissions": [perm.to_dict() for perm in permissions]
                }

                # Cache the result
                await cache.set(cache_key, json.dumps(role_dict), expire=60)
                return permissions
        except IntegrityError:
            raise
        except Exception:
            raise
