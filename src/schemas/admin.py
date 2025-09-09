from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re

class AdminRole(str, Enum):
    """管理员角色枚举"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"

class AdminCreate(BaseModel):
    """创建管理员请求模型"""
    username: str = Field(..., min_length=1, max_length=50, description="管理员用户名")
    email: EmailStr = Field(..., description="管理员邮箱")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    role: Optional[AdminRole] = Field(AdminRole.ADMIN, description="管理员角色")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('用户名不能为空')
        if not re.match(r'^[\w\s\-\.]+$', v):
            raise ValueError('用户名只能包含字母、数字、空格、下划线、连字符和点')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v and not re.match(r'^[\d\-\+\(\)\s]+$', v):
                raise ValueError('手机号格式不正确')
        return v

class AdminUpdate(BaseModel):
    """更新管理员请求模型"""
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[AdminRole] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('用户名不能为空')
            if not re.match(r'^[\w\s\-\.]+$', v):
                raise ValueError('用户名只能包含字母、数字、空格、下划线、连字符和点')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v and not re.match(r'^[\d\-\+\(\)\s]+$', v):
                raise ValueError('手机号格式不正确')
        return v

class AdminUpdatePassword(BaseModel):
    """更新管理员密码请求模型"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")

class AdminLogin(BaseModel):
    """管理员登录请求模型"""
    email: EmailStr = Field(..., description="管理员邮箱")
    password: str = Field(..., description="密码")

class AdminOut(BaseModel):
    """管理员输出模型"""
    id: int
    uid: str
    username: str
    email: str
    phone: Optional[str]
    role: AdminRole
    created_time: datetime
    updated_time: datetime
    last_login_time: Optional[datetime]
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "uid": "550e8400-e29b-41d4-a716-446655440000",
                "username": "admin",
                "email": "admin@example.com",
                "phone": "13800138000",
                "role": "admin",
                "created_time": "2023-01-01T12:00:00",
                "updated_time": "2023-01-01T12:00:00",
                "last_login_time": "2023-01-01T12:00:00"
            }
        }

class AdminListResponse(BaseModel):
    """管理员列表响应模型"""
    total: int = Field(..., description="总数量")
    items: List[AdminOut] = Field(..., description="管理员列表")
    skip: int = Field(..., description="跳过数量")
    limit: int = Field(..., description="限制数量")

class AdminSearchParams(BaseModel):
    """管理员搜索参数模型"""
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[AdminRole] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class AdminToken(BaseModel):
    """管理员Token响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    admin_info: AdminOut