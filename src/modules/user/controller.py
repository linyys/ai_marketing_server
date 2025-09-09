from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from crud.user import (
    create_user, get_user_by_id, get_user_by_email, get_user_by_uid, get_users, get_users_count,
    update_user, update_user_password, soft_delete_user, authenticate_user,
    search_users, get_users_by_role
)
from schemas.user import (
    UserCreate, UserUpdate, UserOut, UserLogin, UserUpdatePassword,
    UserSearchParams, UserListResponse, PaginationParams
)

from typing import List
import logging

logger = logging.getLogger(__name__)

def register_user(db: Session, user_data: UserCreate) -> UserOut:
    """用户注册"""
    try:
        user = create_user(db, user_data)
        return UserOut.from_orm(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户失败"
        )

def login_user(db: Session, login_data: UserLogin) -> UserOut:
    """用户登录"""
    try:
        user = authenticate_user(db, login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        return UserOut.from_orm(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败"
        )

def get_user_info(db: Session, user_id: int) -> UserOut:
    """获取用户信息"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return UserOut.from_orm(user)

def get_user_info_by_uid(db: Session, uid: str) -> UserOut:
    """根据UID获取用户信息"""
    user = get_user_by_uid(db, uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return UserOut.from_orm(user)

def update_user_info(db: Session, user_id: int, update_data: UserUpdate) -> UserOut:
    """更新用户信息"""
    try:
        user = update_user(db, user_id, update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return UserOut.from_orm(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户信息失败"
        )

def change_user_password(db: Session, user_id: int, password_data: UserUpdatePassword) -> dict:
    """修改用户密码"""
    try:
        success = update_user_password(
            db, user_id, password_data.old_password, password_data.new_password
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return {"message": "密码修改成功"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating password for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码修改失败"
        )

def delete_user(db: Session, user_id: int) -> dict:
    """删除用户"""
    try:
        success = soft_delete_user(db, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return {"message": "用户删除成功"}
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户失败"
        )

def get_users_list(db: Session, pagination: PaginationParams) -> UserListResponse:
    """获取用户列表"""
    try:
        skip = (pagination.page - 1) * pagination.page_size
        users = get_users(db, skip=skip, limit=pagination.page_size)
        total = get_users_count(db)
        
        user_list = [UserOut.from_orm(user) for user in users]
        
        return UserListResponse(
            users=user_list,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size
        )
    except Exception as e:
        logger.error(f"Error getting users list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表失败"
        )

def search_users_list(db: Session, search_params: UserSearchParams, pagination: PaginationParams) -> UserListResponse:
    """搜索用户"""
    try:
        skip = (pagination.page - 1) * pagination.page_size
        users, total = search_users(db, search_params, skip=skip, limit=pagination.page_size)
        
        user_list = [UserOut.from_orm(user) for user in users]
        
        return UserListResponse(
            users=user_list,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size
        )
    except Exception as e:
        logger.error(f"Error searching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="搜索用户失败"
        )


    """根据角色获取用户列表"""
    try:
        skip = (pagination.page - 1) * pagination.page_size
        users = get_users_by_role(db, role, skip=skip, limit=pagination.page_size)
        
        # 获取该角色的用户总数
        from sqlalchemy import and_
        from db.user import User
        total = db.query(User).filter(
            and_(User.role == role, User.is_del == 0)
        ).count()
        
        user_list = [UserOut.from_orm(user) for user in users]
        
        return UserListResponse(
            users=user_list,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size
        )
    except Exception as e:
        logger.error(f"Error getting users by role {role}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色用户列表失败"
        )

def verify_user_email(db: Session, email: str) -> dict:
    """验证邮箱是否已存在"""
    try:
        user = get_user_by_email(db, email)
        return {"exists": user is not None}
    except Exception as e:
        logger.error(f"Error verifying email {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证邮箱失败"
        )
