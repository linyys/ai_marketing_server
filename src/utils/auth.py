#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证相关工具函数
"""

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db.database import get_db
from crud.user import get_user_by_uid
from crud.admin import get_admin_by_uid
from utils.jwt_utils import verify_token

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

def get_current_user(optional: bool = False):
    """获取当前用户，支持可选认证
    
    Args:
        optional: 是否启用可选认证模式。设置为True时，未提供认证凭据将返回None，而不是抛出异常。
        适用于需要同时支持匿名访问和登录用户访问的接口。
        
    Returns:
        用户对象或None（当optional=True且未提供有效认证时）
    """
    # 根据optional参数选择合适的security依赖
    def dependency(credentials: HTTPAuthorizationCredentials = Depends(security_optional if optional else security)):
        if not credentials:
            if optional:
                return None
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未提供认证凭据"
            )
        
        try:
            token_data = verify_token(credentials.credentials)
            if not token_data:
                if optional:
                    return None
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的认证凭据"
                )
            
            db = next(get_db())
            user = get_user_by_uid(db, token_data.uid)
            db.close()
            
            if not user:
                if optional:
                    return None
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户不存在"
                )
            
            return user
        except Exception as e:
            if optional:
                return None
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="认证失败"
            )
    
    return dependency

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