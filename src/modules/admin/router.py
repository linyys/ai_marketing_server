from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.admin import (
    AdminCreate, AdminUpdate, AdminOut, AdminLogin, AdminUpdatePassword,
    AdminSearchParams, AdminListResponse, AdminToken
)
from utils.auth import get_current_admin
from utils.exceptions import (
    ValidationException, AuthenticationException, NotFoundException,
    ConflictException, DatabaseException
)
from crud.admin import (
    get_admin_by_email, get_admin_by_uid, get_admins, get_admins_count,
    authenticate_admin, search_admins, create_admin
)
from utils.jwt_utils import create_access_token, get_token_expire_time
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["管理员管理"])

@router.post("/register", response_model=AdminOut, summary="管理员注册")
def admin_register(
    admin_data: AdminCreate,
    db: Session = Depends(get_db)
):
    """
    管理员注册接口
    
    - **username**: 管理员用户名
    - **email**: 管理员邮箱
    - **password**: 密码
    - **phone**: 手机号（可选）

    """
    try:
        logger.info(f"尝试注册管理员: {admin_data.email}")
        admin = create_admin(
            db=db,
            username=admin_data.username,
            email=admin_data.email,
            password=admin_data.password,
            phone=admin_data.phone
        )
        logger.info(f"管理员注册成功: {admin.email}")
        return admin
    except ValueError as e:
        logger.warning(f"管理员注册失败 - 数据验证错误: {str(e)}")
        raise ValidationException(str(e))
    except Exception as e:
        logger.error(f"管理员注册失败 - 系统错误: {str(e)}")
        raise DatabaseException("注册失败，请稍后重试")

@router.post("/login", response_model=AdminToken, summary="管理员登录")
def admin_login(
    login_data: AdminLogin,
    db: Session = Depends(get_db)
):
    """
    管理员登录接口
    
    - **email**: 管理员邮箱
    - **password**: 密码
    """
    try:
        logger.info(f"尝试登录: {login_data.email}")
        admin = authenticate_admin(db, login_data.email, login_data.password)
        if not admin:
            logger.warning(f"登录失败 - 认证错误: {login_data.email}")
            raise AuthenticationException("邮箱或密码错误")
        
        # 生成JWT token
        access_token = create_access_token(data={"sub": admin.uid, "is_admin": True})
        expires_in = get_token_expire_time()
        
        logger.info(f"登录成功: {admin.email}")
        return AdminToken(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            admin_info=AdminOut.model_validate(admin)
        )
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"登录失败 - 系统错误: {str(e)}")
        raise DatabaseException("登录失败，请稍后重试")

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
    try:
        logger.info(f"查询管理员信息: ID={admin_id}")
        admins, _ = search_admins(db, admin_id=admin_id, skip=0, limit=1)
        if not admins:
            logger.warning(f"管理员不存在: ID={admin_id}")
            raise NotFoundException("管理员不存在")
        return admins[0]
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"查询管理员失败: ID={admin_id}, 错误={str(e)}")
        raise DatabaseException("查询管理员信息失败")

@router.get("/uid/{uid}", response_model=AdminOut, summary="根据UID获取管理员信息")
def get_admin_by_uid(
    uid: str = Path(..., description="管理员UID"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    根据UID获取管理员信息（需要管理员权限）
    """
    try:
        logger.info(f"根据UID查询管理员: {uid}")
        admin = get_admin_by_uid(db, uid)
        if not admin:
            logger.warning(f"管理员不存在: UID={uid}")
            raise NotFoundException("管理员不存在")
        return admin
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"根据UID查询管理员失败: UID={uid}, 错误={str(e)}")
        raise DatabaseException("查询管理员信息失败")



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
    try:
        logger.info(f"获取管理员列表: page={page}, page_size={page_size}")
        skip = (page - 1) * page_size
        admins = get_admins(db, skip, page_size)
        total = get_admins_count(db)
        
        return AdminListResponse(
            total=total,
            items=admins,
            skip=skip,
            limit=page_size
        )
    except Exception as e:
        logger.error(f"获取管理员列表失败: {str(e)}")
        raise DatabaseException("获取管理员列表失败")