from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.users import Roles
from app.routers.auth import get_current_active_user
from app.schemas.roles import RoleBase
from app.services.roles_service import RoleService

router = APIRouter()


@router.get("/roles/{role_id}", response_model=Roles)
async def read_roles_by_Id(role_id: int, current_user: dict = Depends(get_current_active_user),
                           session: AsyncSession = Depends(get_session)):
    db_role = RoleService.service_get_role_by_id(role_id, session)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role


@router.get("/roles/{role_name}", response_model=Roles)
async def read_roles_by_Name(role_name: str, current_user: dict = Depends(get_current_active_user),
                             session: AsyncSession = Depends(get_session)):
    db_role = RoleService.service_get_role_by_name(role_name, session)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    return db_role


@router.post("/roles/", response_model=Roles, status_code=status.HTTP_201_CREATED)
async def create_role(role: RoleBase, session: AsyncSession = Depends(get_session)):
    db_role = await RoleService.service_create_role(role, session)
    return db_role


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: int,
                      current_user: dict = Depends(get_current_active_user)):
    db_role = read_roles_by_Id(role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    db_deleted = RoleService.service_delete_role(role_id)
    if db_deleted is None:
        raise HTTPException(status_code=409,
                            detail="Role logical constraints")
    return


@router.put("/roles/{role_id}", response_model=Roles)
async def update_user(role_id: int, role: RoleBase,
                      current_user: dict = Depends(get_current_active_user)):
    return RoleService.service_update_role(role_id, role)
