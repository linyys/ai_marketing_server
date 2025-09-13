from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.user import (
    UserCreate, UserUpdate, UserOut, UserLogin, UserUpdatePassword,
    UserListResponse, UserSearchParams, Token
)
from modules.user.controller import (
    register_user_service, login_user_service, get_user_service,
    get_users_list_service, update_user_service, delete_user_service,
    search_users_service, update_password_service
)
from utils.auth import get_current_admin_or_user, get_current_user, get_current_admin
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["用户"], prefix="/user")

@router.post("/register", response_model=UserOut, summary="用户注册")
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """用户注册接口"""
    logger.info(f"用户注册请求: {user_data.email}")
    return register_user_service(db, user_data)

@router.post("/login", response_model=Token, summary="用户登录")
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """用户登录接口"""
    logger.info(f"用户登录请求: {login_data.email}")
    return login_user_service(db, login_data)

@router.get("/list", response_model=UserListResponse, summary="获取用户列表")
def get_users_list(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """获取用户列表接口（仅管理员可访问）"""
    logger.info(f"管理员 {current_admin.username} 请求用户列表")
    return get_users_list_service(db, skip, limit)

@router.get("/get/{uid}", response_model=UserOut, summary="获取指定用户信息")
def get_user(
    uid: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    """获取指定用户信息接口（管理员或本人可访问）"""
    # 检查权限：管理员或本人
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    
    if is_admin:
        logger.info(f"管理员 {current_user.username} 请求用户信息: {uid}")
    else:
        # 非管理员，检查是否为本人
        if uid != current_user.uid:
            logger.warning(f"用户 {current_user.uid} 尝试访问其他用户信息: {uid}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限访问其他用户信息"
            )
        logger.info(f"用户 {current_user.uid} 请求自己的信息")
    
    return get_user_service(db, uid)

@router.post("/search", response_model=UserListResponse, summary="搜索用户")
def search_users(
    search_params: UserSearchParams,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """搜索用户接口（仅管理员可访问）"""
    logger.info(f"管理员 {current_admin.username} 搜索用户")
    return search_users_service(db, search_params, skip, limit)

@router.post("/update", response_model=UserOut, summary="更新用户信息")
def update_user(
    uid: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """更新用户信息接口（仅管理员可访问）"""
    logger.info(f"管理员 {current_admin.username} 更新用户信息: {uid}")
    return update_user_service(db, uid, user_data)

@router.post("/delete", summary="删除用户")
def delete_user(
    uid: str,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """删除用户接口（仅管理员可访问）"""
    logger.info(f"管理员 {current_admin.username} 删除用户: {uid}")
    return delete_user_service(db, uid)

@router.post("/update/password", summary="修改密码")
def update_password(
    uid: str,
    password_data: UserUpdatePassword,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """修改密码接口（管理员或本人可访问）"""
    # 检查权限：管理员或本人
    try:
        # 尝试获取管理员权限
        from utils.auth import get_current_admin
        admin = get_current_admin()
        logger.info(f"管理员 {admin.username} 修改用户密码: {uid}")
    except:
        # 非管理员，检查是否为本人
        if uid != current_user.uid:
            logger.warning(f"用户 {current_user.uid} 尝试修改其他用户密码: {uid}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改其他用户密码"
            )
        logger.info(f"用户 {current_user.uid} 修改自己的密码")
    
    return update_password_service(db, uid, password_data, current_user.uid)