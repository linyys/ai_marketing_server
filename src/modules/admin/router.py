from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.admin import (
    AdminCreate, AdminUpdate, AdminOut, AdminLogin, AdminUpdatePassword,
    AdminSearchParams, AdminListResponse, AdminRole
)
from utils.auth import get_current_admin
from crud.admin import (
    get_admin_by_id, get_admin_by_email, get_admin_by_uid, get_admins,
    authenticate_admin, get_admins_by_role
)
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["管理员管理"])

@router.post("/login", response_model=AdminOut, summary="管理员登录")
def admin_login(
    login_data: AdminLogin,
    db: Session = Depends(get_db)
):
    """
    管理员登录接口
    
    - **email**: 管理员邮箱
    - **password**: 密码
    """
    admin = authenticate_admin(db, login_data.email, login_data.password)
    if not admin:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )
    return admin

@router.get("/profile", response_model=AdminOut, summary="获取当前管理员信息")
def get_admin_profile(
    current_admin = Depends(get_current_admin)
):
    """
    获取当前登录管理员的信息
    """
    return current_admin

@router.get("/{admin_id}", response_model=AdminOut, summary="获取管理员信息")
def get_admin(
    admin_id: int = Path(..., description="管理员ID"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    获取管理员信息（需要管理员权限）
    """
    admin = get_admin_by_id(db, admin_id)
    if not admin:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )
    return admin

@router.get("/uid/{uid}", response_model=AdminOut, summary="根据UID获取管理员信息")
def get_admin_by_uid(
    uid: str = Path(..., description="管理员UID"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    根据UID获取管理员信息（需要管理员权限）
    """
    admin = get_admin_by_uid(db, uid)
    if not admin:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="管理员不存在"
        )
    return admin

@router.get("/", response_model=AdminListResponse, summary="获取管理员列表")
def get_admins_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    获取管理员列表（需要管理员权限）
    """
    skip = (page - 1) * page_size
    admins = get_admins(db, skip, page_size)
    total = len(admins)
    
    return AdminListResponse(
        total=total,
        items=admins,
        skip=skip,
        limit=page_size
    )

@router.get("/role/{role}", response_model=AdminListResponse, summary="根据角色获取管理员列表")
def get_admins_by_role_list(
    role: AdminRole = Path(..., description="管理员角色"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    根据角色获取管理员列表（需要管理员权限）
    """
    skip = (page - 1) * page_size
    admins = get_admins_by_role(db, role, skip, page_size)
    total = len(admins)
    
    return AdminListResponse(
        total=total,
        items=admins,
        skip=skip,
        limit=page_size
    )