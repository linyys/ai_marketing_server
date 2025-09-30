from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

class UserCreate(BaseModel):
    """创建用户请求模型"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")

    
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

class UserUpdate(BaseModel):
    """更新用户请求模型"""
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)

    
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

class UserUpdatePassword(BaseModel):
    """更新密码请求模型"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")

class UserLogin(BaseModel):
    """用户登录请求模型"""
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., description="密码")

class UserOut(BaseModel):
    """用户输出模型"""
    uid: str
    username: str
    email: str
    phone: Optional[str]
    created_time: datetime
    updated_time: datetime
    last_login_time: Optional[datetime]
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "uid": "550e8400-e29b-41d4-a716-446655440000",
                "username": "张三",
                "email": "zhangsan@example.com",
                "phone": "13800138000",
                "created_time": "2023-01-01T12:00:00",
                "updated_time": "2023-01-01T12:00:00",
                "last_login_time": "2023-01-01T12:00:00"
            }
        }

class UserListResponse(BaseModel):
    """用户列表响应模型"""
    total: int = Field(..., description="总数量")
    items: List[UserOut] = Field(..., description="用户列表")
    skip: int = Field(..., description="跳过数量")
    limit: int = Field(..., description="限制数量")

class UserSearchParams(BaseModel):
    """用户搜索参数模型"""
    username: Optional[str] = None
    email: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: UserOut

class PaginationParams(BaseModel):
    """分页参数模型"""
    skip: int = Field(0, ge=0, description="跳过记录数")
    limit: int = Field(20, ge=1, le=100, description="返回记录数限制")