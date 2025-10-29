#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证相关工具函数
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db.database import get_db
from crud.user import get_user_by_uid, get_user_by_phone
from crud.admin import get_admin_by_uid, get_admin_by_phone
from utils.jwt_utils import verify_token
from utils.http_request import create_post

security = HTTPBearer()

EXTERNAL_BASE_URL = "https://www.baikexue.cn"
EXTERNAL_HEADERS = {"Content-Type": "application/json"}

async def _check_external_token(raw_token: str) -> dict:
    """调用外部接口校验 token，返回外部响应 JSON"""
    post = create_post(EXTERNAL_BASE_URL, EXTERNAL_HEADERS)
    payload = {"action": "checkToken", "token": raw_token}
    resp = await post("/api/agent/user.php", json=payload)
    return resp or {}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    获取当前认证用户（强制认证）
    
    返回：
        当前用户对象
    异常：
        认证失败抛出401
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
        
        user = get_user_by_uid(db, user_id)
        if user is None:
            raise credentials_exception
        
        return user
    except HTTPException:
        raise
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

# 新增：外部 token 鉴权函数（不修改现有函数）
async def get_external_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 优先尝试本地短期通行证（JWT）验证
        local_payload = verify_token(credentials.credentials)
        if local_payload:
            user_id = local_payload.get("sub")
            if user_id:
                user = get_user_by_uid(db, user_id)
                if user is not None:
                    return user
        # 未命中本地JWT，回源外部校验
        resp = await _check_external_token(credentials.credentials)
        if not resp or resp.get("code") != 200:
            raise credentials_exception
        data = resp.get("data") or {}
        phone = str(data.get("phone") or "")
        if not phone:
            raise credentials_exception
        user = get_user_by_phone(db, phone)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="未绑定本地用户，请联系管理员或先绑定手机号",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception

async def get_external_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
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
        # 优先尝试本地短期通行证（JWT）验证
        local_payload = verify_token(credentials.credentials)
        if local_payload:
            is_admin = local_payload.get("is_admin")
            admin_id = local_payload.get("sub")
            if is_admin and admin_id:
                admin = get_admin_by_uid(db, admin_id)
                if admin is not None:
                    return admin
        # 未命中本地JWT，回源外部校验
        resp = await _check_external_token(credentials.credentials)
        if not resp or resp.get("code") != 200:
            raise credentials_exception
        data = resp.get("data") or {}
        phone = str(data.get("phone") or "")
        if not phone:
            raise credentials_exception
        admin = get_admin_by_phone(db, phone)
        if admin is None:
            raise permission_exception
        return admin
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception

async def get_external_current_admin_or_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 优先尝试本地短期通行证（JWT）验证
        local_payload = verify_token(credentials.credentials)
        if local_payload:
            user_id = local_payload.get("sub")
            is_admin = local_payload.get("is_admin", False)
            if user_id:
                if is_admin:
                    admin = get_admin_by_uid(db, user_id)
                    if admin is not None:
                        return admin
                else:
                    user = get_user_by_uid(db, user_id)
                    if user is not None:
                        return user
        # 未命中本地JWT，回源外部校验
        resp = await _check_external_token(credentials.credentials)
        if not resp or resp.get("code") != 200:
            raise credentials_exception
        data = resp.get("data") or {}
        phone = str(data.get("phone") or "")
        if not phone:
            raise credentials_exception
        admin = get_admin_by_phone(db, phone)
        if admin is not None:
            return admin
        user = get_user_by_phone(db, phone)
        if user is not None:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="未绑定本地账户，请联系管理员或先绑定手机号",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception