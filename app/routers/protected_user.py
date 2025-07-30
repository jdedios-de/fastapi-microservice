from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.dependencies import get_cache, get_tracer
from app.models.users import UserRoles
from app.routers.auth import get_current_active_user
from app.schemas.role_permission import RolePermission
from app.schemas.user_profile import UserProfileBase, UserProfile

from app.schemas.user import UserCreate, UserUpdate, User
from app.schemas.user_roles import UserRole
from app.services.user_service import UserService

router = APIRouter()


@router.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int, session: AsyncSession = Depends(get_session), cache=Depends(get_cache),
                    tracer=Depends(get_tracer)):
    db_user = await UserService.get_user_by_id(user_id, session, cache, tracer)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


@router.post("/users/", response_model=User,
             status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_session), tracer=Depends(get_tracer)):
    try:
        return await UserService.service_create_user(user, session, tracer)
    except Exception:
        raise


@router.post("/users/profile", response_model=UserProfile,
             status_code=status.HTTP_201_CREATED)
async def create_user_profile(user_profile: UserProfileBase):
    return UserService.service_create_user_profile(user_profile)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int,
                      current_user: dict = Depends(get_current_active_user)):
    db_user = UserService.get_user_by_id(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_deleted = UserService.service_delete_user(user_id)
    if db_deleted is None:
        raise HTTPException(status_code=409,
                            detail="User logical constraints")
    return


@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate,
                      current_user: dict = Depends(get_current_active_user)):
    return UserService.service_update_user(user_id, user)


@router.post("/users/assign_roles", response_model=UserRoles,
             status_code=status.HTTP_201_CREATED)
async def user_assign_roles(user_roles: UserRole, session: AsyncSession = Depends(get_session)):
    return await UserService.service_assign_role(user_roles, session)


@router.post("/users/assign_permission", response_model=RolePermission,
             status_code=status.HTTP_201_CREATED)
async def assign_permission(role_permission: RolePermission, session: AsyncSession = Depends(get_session)):
    return await UserService.service_assign_permission(role_permission, session)
