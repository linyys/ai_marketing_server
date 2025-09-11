from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from crud.user import (
    create_user, get_user_by_uid, get_users, get_users_count,
    update_user, delete_user, search_users, authenticate_user,
    update_user_last_login, update_user_password, verify_password
)
from schemas.user import (
    UserCreate, UserUpdate, UserOut, UserLogin, UserUpdatePassword,
    UserListResponse, UserSearchParams, Token, PaginationParams
)
from utils.jwt_utils import create_access_token
from typing import List
import logging

logger = logging.getLogger(__name__)

def register_user_service(db: Session, user_data: UserCreate) -> UserOut:
    """用户注册服务"""
    try:
        user = create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            phone=user_data.phone
        )
        return UserOut.model_validate(user)
    except ValueError as e:
        logger.warning(f"用户注册失败 - 数据验证错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"用户注册失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户注册失败，请稍后重试"
        )

def login_user_service(db: Session, login_data: UserLogin) -> Token:
    """用户登录服务"""
    try:
        user = authenticate_user(db, login_data.email, login_data.password)
        if not user:
            logger.warning(f"用户登录失败: 邮箱或密码错误 - {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        
        # 更新最后登录时间
        update_user_last_login(db, user.uid)
        
        # 生成访问令牌
        access_token = create_access_token(
            data={"sub": user.uid, "email": user.email, "role": "user", "is_admin": False}
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600,
            user_info=UserOut.model_validate(user)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )

def get_user_service(db: Session, uid: str) -> UserOut:
    """获取用户服务"""
    try:
        user = get_user_by_uid(db, uid)
        if not user:
            logger.warning(f"用户不存在: UID={uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return UserOut.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败，请稍后重试"
        )

def get_users_list_service(
    db: Session,
    skip: int = 0,
    limit: int = 20
) -> UserListResponse:
    """获取用户列表服务"""
    try:
        users = get_users(db, skip=skip, limit=limit)
        total = get_users_count(db)
        
        return UserListResponse(
            total=total,
            items=[UserOut.model_validate(user) for user in users],
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"获取用户列表失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表失败，请稍后重试"
        )

def update_user_service(
    db: Session,
    uid: str,
    user_data: UserUpdate
) -> UserOut:
    """更新用户服务"""
    try:
        user = update_user(
            db=db,
            user_uid=uid,
            username=user_data.username,
            email=user_data.email,
            phone=user_data.phone
        )
        if not user:
            logger.warning(f"用户不存在: UID={uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return UserOut.model_validate(user)
    except ValueError as e:
        logger.warning(f"更新用户失败 - 数据验证错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户失败，请稍后重试"
        )

def delete_user_service(db: Session, uid: str) -> dict:
    """删除用户服务"""
    try:
        success = delete_user(db, uid)
        if not success:
            logger.warning(f"用户不存在: UID={uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        logger.info(f"用户删除成功: UID={uid}")
        return {"message": "用户删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除用户失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户失败，请稍后重试"
        )

def search_users_service(
    db: Session,
    search_params: UserSearchParams,
    skip: int = 0,
    limit: int = 20
) -> UserListResponse:
    """搜索用户服务"""
    try:
        users, total = search_users(
            db=db,
            username=search_params.username,
            email=search_params.email,
            start_time=search_params.start_time,
            end_time=search_params.end_time,
            skip=skip,
            limit=limit
        )
        
        return UserListResponse(
            total=total,
            items=[UserOut.model_validate(user) for user in users],
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"搜索用户失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="搜索用户失败，请稍后重试"
        )

def update_password_service(
    db: Session,
    uid: str,
    password_data: UserUpdatePassword,
    current_user_uid: str
) -> dict:
    """修改密码服务"""
    try:
        # 获取用户信息
        user = get_user_by_uid(db, uid)
        if not user:
            logger.warning(f"用户不存在: UID={uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证旧密码（只有本人修改时需要验证）
        if uid == current_user_uid:
            if not verify_password(password_data.old_password, user.password_hash):
                logger.warning(f"修改密码失败: 原密码错误 - UID={uid}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="原密码错误"
                )
        
        # 更新密码
        success = update_user_password(db, uid, password_data.new_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="密码更新失败"
            )
        
        logger.info(f"密码修改成功: UID={uid}")
        return {"message": "密码修改成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败，请稍后重试"
        )