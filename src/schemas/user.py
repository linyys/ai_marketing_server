from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
import re

class UserCreate(BaseModel):
    """创建用户请求模型"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
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
    phone: str = Field(..., min_length=3, max_length=20, description="手机号")
    password: str = Field(..., description="密码")

class UserOut(BaseModel):
    """用户输出模型"""
    id: int
    uid: str
    username: str
    phone: Optional[str]
    avatar: Optional[str] = None
    point: Decimal
    created_time: datetime
    updated_time: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "uid": "550e8400-e29b-41d4-a716-446655440000",
                "username": "张三",
                "phone": "13800138000",
                "avatar": "https://example.com/avatar.jpg",
                "created_time": "2023-01-01T12:00:00",
                "updated_time": "2023-01-01T12:00:00",
                "point": 1000
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
    phone: Optional[str] = None
    point: Optional[Decimal] = None
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

# ==========================
# 外部用户认证相关模型（百科学）
# ==========================

class ExternalSendSmsRequest(BaseModel):
    """外部接口-发送验证码请求模型"""
    phone: str = Field(..., description="手机号")

class ExternalSendSmsResponse(BaseModel):
    """外部接口-发送验证码响应模型"""
    code: int
    txt: Optional[str] = None

class ExternalLoginRequest(BaseModel):
    """外部接口-登录请求模型"""
    state: int = Field(..., description="1：验证码登录 2：密码登录")
    phone: str = Field(..., description="手机号")
    code: Optional[str] = Field(None, description="验证码（state=1时必填）")
    password: Optional[str] = Field(None, description="密码（state=2时必填）")

class ExternalUserInfo(BaseModel):
    """外部接口-用户信息数据模型"""
    id: str
    phone: str
    avatar: Optional[str] = None
    nickname: Optional[str] = None
    name: Optional[str] = None
    token: str

class ExternalLoginResponse(BaseModel):
    """外部接口-登录响应模型"""
    code: int
    txt: Optional[str] = None
    data: Optional[ExternalUserInfo] = None
    # 本地短期通行证（可选）：当外部token有效且手机号已绑定本地用户时返回
    local_access_token: Optional[str] = None
    local_expires_in: Optional[int] = None

class ExternalSetPasswordRequest(BaseModel):
    """外部接口-初次设置密码请求模型"""
    token: str = Field(..., description="登录token")
    password: str = Field(..., min_length=8, description="密码（8位以上）")
    password2: str = Field(..., min_length=8, description="确认密码（8位以上）")

class ExternalBaseResponse(BaseModel):
    """外部接口-通用响应模型"""
    code: int
    txt: Optional[str] = None

class ExternalCheckTokenRequest(BaseModel):
    """外部接口-检查登录状态请求模型"""
    token: str = Field(..., description="登录token")

class ExternalCheckTokenResponse(BaseModel):
    """外部接口-检查登录状态响应模型"""
    code: int
    txt: Optional[str] = None
    data: Optional[ExternalUserInfo] = None
    # 本地短期通行证（可选）：当外部token有效且手机号已绑定本地用户时返回
    local_access_token: Optional[str] = None
    local_expires_in: Optional[int] = None