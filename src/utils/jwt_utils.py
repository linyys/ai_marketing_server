#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT token 工具函数
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from jwt.exceptions import PyJWTError
from db.config import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
    
    Returns:
        编码后的JWT令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algo)
    return encoded_jwt

def verify_token(token: str):
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌
    
    Returns:
        解码后的数据，如果验证失败返回None
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algo])
        return payload
    except PyJWTError:
        return None

def get_token_expire_time():
    """
    获取token过期时间（秒）
    """
    return settings.token_expire_minutes * 60