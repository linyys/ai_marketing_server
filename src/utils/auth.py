#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证相关工具函数
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db.database import get_db
from crud.user import get_user_by_uid
from db.user import UserRole
from utils.jwt_utils import verify_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    获取当前认证用户
    
    Args:
        credentials: HTTP Bearer 认证凭据
        db: 数据库会话
    
    Returns:
        当前用户对象
    
    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 验证token
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        # 获取用户ID
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # 查询用户
        user = get_user_by_uid(db, user_id)
        if user is None:
            raise credentials_exception
        
        return user
    
    except Exception:
        raise credentials_exception

def get_current_user_uid(current_user = Depends(get_current_user)) -> str:
    """
    获取当前用户的UID
    
    Args:
        current_user: 当前用户对象
    
    Returns:
        用户UID
    """
    return current_user.uid

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    获取当前认证管理员
    
    Args:
        credentials: HTTP Bearer 认证凭据
        db: 数据库会话
    
    Returns:
        当前管理员用户对象
    
    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    permission_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="无管理员权限",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 验证token
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        # 获取用户ID
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # 查询用户
        user = get_user_by_uid(db, user_id)
        if user is None:
            raise credentials_exception
        
        # 检查用户角色
        if user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            print(f"User {user.username} attempted admin access with role: {user.role}")
            raise permission_exception
        
        return user
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise credentials_exception


def get_current_user_or_admin(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    获取当前认证用户或管理员
    
    此函数允许普通用户或管理员访问，不限制角色
    
    Args:
        credentials: HTTP Bearer 认证凭据
        db: 数据库会话
    
    Returns:
        当前用户对象
    
    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 验证token
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        # 获取用户ID
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # 查询用户
        user = get_user_by_uid(db, user_id)
        if user is None:
            raise credentials_exception
        
        return user
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise credentials_exception