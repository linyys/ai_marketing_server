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
from crud.admin import get_admin_by_uid
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



def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    获取当前认证管理员
    
    Args:
        credentials: HTTP Bearer 认证凭据
        db: 数据库会话
    
    Returns:
        当前管理员对象
    
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
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        is_admin = payload.get("is_admin")
        if not is_admin:
            raise permission_exception
        
        admin_id: str = payload.get("sub")
        if admin_id is None:
            raise credentials_exception
        
        admin = get_admin_by_uid(db, admin_id)
        if admin is None:
            raise credentials_exception
        
        return admin
    
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception


def get_current_admin_or_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    获取当前认证管理员或用户
    
    根据token中的is_admin标识判断身份类型，然后查询对应的表
    
    Args:
        credentials: HTTP Bearer 认证凭据
        db: 数据库会话
    
    Returns:
        当前管理员或用户对象
    
    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        is_admin = payload.get("is_admin", False)
        
        if is_admin:
            admin = get_admin_by_uid(db, user_id)
            if admin is None:
                raise credentials_exception
            return admin
        else:
            user = get_user_by_uid(db, user_id)
            if user is None:
                raise credentials_exception
            return user
    
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception