from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.users import Permissions
from app.routers.auth import get_current_active_user
from app.schemas.permissions import PermissionBase
from app.services.permissions_service import PermissionService

router = APIRouter()


@router.get("/permissions/{permission_id}", response_model=Permissions)
async def get_permission_by_Id(permission_id: int,current_user: dict = Depends(get_current_active_user)):
    db_permission = PermissionService.service_get_permission_by_id(permission_id)
    if db_permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")

    return db_permission


@router.get("/permissions/{permission_name}", response_model=Permissions)
async def get_permission_by_Name(permission_name: str,current_user: dict = Depends(get_current_active_user)):
    db_permission = PermissionService.service_get_permission_by_name(permission_name)
    if db_permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")

    return db_permission


@router.post("/permissions/", response_model=Permissions,
             status_code=status.HTTP_201_CREATED)
async def create_permission(permission: PermissionBase, session: AsyncSession = Depends(get_session)):
    db_permission = await PermissionService.service_create_permission(permission, session)
    return db_permission


@router.delete("/permissions/{permission_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(permission_id: int,
                            current_user: dict = Depends(
                                get_current_active_user)):
    db_permission = get_permission_by_Id(permission_id)
    if db_permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    db_permission = PermissionService.service_delete_permission(permission_id)
    if db_permission is None:
        raise HTTPException(status_code=409,
                            detail="Permission logical constraints")
    return


@router.put("/permissions/{permission_id}", response_model=Permissions)
async def update_permission(permission_id: int, permission: PermissionBase,
                            current_user: dict = Depends(
                                get_current_active_user)):
    return PermissionService.service_update_permission(permission_id, permission)
