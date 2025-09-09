from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.user import (
    UserCreate, UserUpdate, UserOut, UserLogin, UserUpdatePassword,
    UserSearchParams, UserListResponse, PaginationParams
)
from modules.user.controller import (
    register_user, login_user, get_user_info, get_user_info_by_uid, update_user_info,
    change_user_password, delete_user, get_users_list, search_users_list,
    get_users_by_role_list, verify_user_email
)
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/user", tags=["用户管理"])

@router.post("/register", response_model=UserOut, summary="用户注册")
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    用户注册接口
    
    - **username**: 用户名（必填，唯一）
    - **email**: 邮箱（必填，唯一）
    - **password**: 密码（必填，至少6位）
    - **phone**: 手机号（可选）

    """
    return register_user(db, user_data)

@router.post("/login", response_model=UserOut, summary="用户登录")
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    
    - **email**: 邮箱
    - **password**: 密码
    """
    return login_user(db, login_data)

@router.get("/{user_id}", response_model=UserOut, summary="获取用户信息")
def get_user(
    user_id: int = Path(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    获取用户信息
    """
    return get_user_info(db, user_id)

@router.get("/uid/{uid}", response_model=UserOut, summary="根据UID获取用户信息")
def get_user_by_uid(
    uid: str = Path(..., description="用户UID"),
    db: Session = Depends(get_db)
):
    """
    根据UID获取用户信息
    """
    return get_user_info_by_uid(db, uid)

@router.put("/{user_id}", response_model=UserOut, summary="更新用户信息")
def update_user(
    user_id: int = Path(..., description="用户ID"),
    update_data: UserUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    
    - **username**: 用户名（可选）
    - **email**: 邮箱（可选）
    - **phone**: 手机号（可选）

    """
    return update_user_info(db, user_id, update_data)

@router.put("/{user_id}/password", summary="修改用户密码")
def update_password(
    user_id: int = Path(..., description="用户ID"),
    password_data: UserUpdatePassword = Body(...),
    db: Session = Depends(get_db)
):
    """
    修改用户密码
    
    - **old_password**: 原密码
    - **new_password**: 新密码（至少6位）
    """
    return change_user_password(db, user_id, password_data)

@router.delete("/{user_id}", summary="删除用户")
def delete_user_by_id(
    user_id: int = Path(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    软删除用户（将is_del标记为1）
    """
    return delete_user(db, user_id)

@router.get("/", response_model=UserListResponse, summary="获取用户列表")
def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（分页）
    
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    """
    pagination = PaginationParams(page=page, page_size=page_size)
    return get_users_list(db, pagination)

@router.get("/search/", response_model=UserListResponse, summary="搜索用户")
def search_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    username: Optional[str] = Query(None, description="用户名（模糊搜索）"),
    email: Optional[str] = Query(None, description="邮箱（模糊搜索）"),

    start_time: Optional[datetime] = Query(None, description="注册开始时间"),
    end_time: Optional[datetime] = Query(None, description="注册结束时间"),
    db: Session = Depends(get_db)
):
    """
    根据条件搜索用户
    
    支持的搜索条件：
    - **username**: 用户名模糊搜索
    - **email**: 邮箱模糊搜索
    - **role**: 用户角色精确匹配
    - **status**: 用户状态（0-禁用，1-启用）
    - **start_time**: 注册开始时间
    - **end_time**: 注册结束时间
    """
    search_params = UserSearchParams(
        username=username,
        email=email,
        role=role,
        start_time=start_time,
        end_time=end_time
    )
    pagination = PaginationParams(page=page, page_size=page_size)
    return search_users_list(db, search_params, pagination)

@router.put("/{user_id}/status", summary="修改用户状态")
def update_user_status(
    user_id: int = Path(..., description="用户ID"),
    status: int = Body(..., embed=True, description="用户状态（0-禁用，1-启用）"),
    db: Session = Depends(get_db)
):
    """
    修改用户状态
    
    - **status**: 0-禁用，1-启用
    """
    return change_user_status(db, user_id, status)



@router.get("/verify/email", summary="验证邮箱是否存在")
def verify_email(
    email: str = Query(..., description="邮箱地址"),
    db: Session = Depends(get_db)
):
    """
    验证邮箱是否已被注册
    
    返回格式：{"exists": true/false}
    """
    return verify_user_email(db, email)

# 批量操作接口
@router.delete("/batch/", summary="批量删除用户")
def batch_delete_users(
    user_ids: list[int] = Body(..., description="用户ID列表"),
    db: Session = Depends(get_db)
):
    """
    批量软删除用户
    
    - **user_ids**: 用户ID列表
    """
    results = []
    for user_id in user_ids:
        try:
            result = delete_user(db, user_id)
            results.append({"user_id": user_id, "success": True, "message": result["message"]})
        except Exception as e:
            results.append({"user_id": user_id, "success": False, "message": str(e)})
    
    return {"results": results}

# 统计接口
@router.get("/stats/overview", summary="用户统计概览")
def get_user_stats(
    db: Session = Depends(get_db)
):
    """
    获取用户统计信息
    
    返回各角色用户数量、总用户数、活跃用户数等统计信息
    """
    from sqlalchemy import func
    from db.user import User
    
    # 总用户数
    total_users = db.query(func.count(User.id)).filter(User.is_del == 0).scalar()
    
    # 各角色用户数
    role_stats = db.query(
        User.role, func.count(User.id).label('count')
    ).filter(User.is_del == 0).group_by(User.role).all()
    

    for role, count in role_stats:
        role_counts[role.value] = count
    
    return {
        "total_users": total_users,
        "role_distribution": role_counts
    }