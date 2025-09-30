from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class RobotCreate(BaseModel):
    """创建机器人请求模型"""
    name: str = Field(..., min_length=1, max_length=50, description="机器人名称")
    reply_type: int = Field(..., ge=0, le=3, description="回复类型：0-评论 1-私信 2-群聊 3-私聊")
    account: Optional[str] = Field(None, max_length=255, description="账号")
    password: Optional[str] = Field(None, max_length=255, description="密码")
    platform: int = Field(..., description="平台：0-微信 1-企业微信 3-抖音 4-小红书")
    login_type: int = Field(..., ge=0, le=1, description="登录类型：0-账号密码登录 1-扫码登录")
    description: str = Field(..., min_length=1, max_length=255, description="描述")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('机器人名称不能为空')
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('描述不能为空')
        return v
    
    @field_validator('platform')
    @classmethod
    def validate_platform(cls, v: int) -> int:
        if v not in [0, 1, 3, 4]:
            raise ValueError('平台值无效')
        return v
    
    @field_validator('reply_type')
    @classmethod
    def validate_reply_type(cls, v: int) -> int:
        if v not in [0, 1, 2, 3]:
            raise ValueError('回复类型值无效')
        return v

class RobotUpdate(BaseModel):
    """更新机器人请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="机器人名称")
    reply_type: Optional[int] = Field(None, ge=0, le=3, description="回复类型：0-评论 1-私信 2-群聊 3-私聊")
    account: Optional[str] = Field(None, max_length=255, description="账号")
    password: Optional[str] = Field(None, max_length=255, description="密码")
    platform: Optional[int] = Field(None, description="平台：0-微信 1-企业微信 3-抖音 4-小红书")
    login_type: Optional[int] = Field(None, ge=0, le=1, description="登录类型：0-账号密码登录 1-扫码登录")
    description: Optional[str] = Field(None, min_length=1, max_length=255, description="描述")
    is_enable: Optional[bool] = Field(None, description="是否启用")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('机器人名称不能为空')
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('描述不能为空')
        return v
    
    @field_validator('platform')
    @classmethod
    def validate_platform(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in [0, 1, 3, 4]:
            raise ValueError('平台值无效')
        return v
    
    @field_validator('reply_type')
    @classmethod
    def validate_reply_type(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in [0, 1, 2, 3]:
            raise ValueError('回复类型值无效')
        return v

class RobotOut(BaseModel):
    """机器人输出模型"""
    uid: str
    name: str
    reply_type: int
    account: Optional[str]
    platform: int
    login_type: int
    description: str
    is_enable: bool
    is_del: bool
    from_user_uid: str
    is_bind_knowledges: bool
    is_bind_filter: bool
    created_time: datetime
    updated_time: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "uid": "550e8400-e29b-41d4-a716-446655440000",
                "name": "客服机器人",
                "reply_type": 3,
                "account": "robot@example.com",
                "platform": 0,
                "login_type": 1,
                "description": "智能客服机器人",
                "is_enable": True,
                "is_del": False,
                "from_user_uid": "user-uid-123",
                "is_bind_knowledges": False,
                "is_bind_filter": False,
                "created_time": "2023-01-01T12:00:00",
                "updated_time": "2023-01-01T12:00:00"
            }
        }

class RobotListResponse(BaseModel):
    """机器人列表响应模型"""
    total: int = Field(..., description="总数量")
    items: List[RobotOut] = Field(..., description="机器人列表")
    skip: int = Field(..., description="跳过数量")
    limit: int = Field(..., description="限制数量")

class RobotSearchParams(BaseModel):
    """机器人搜索参数模型"""
    name: Optional[str] = Field(None, description="机器人名称")
    platform: Optional[int] = Field(None, description="平台")
    is_enable: Optional[bool] = Field(None, description="是否启用")
    from_user_uid: Optional[str] = Field(None, description="用户UID")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")

class RobotDeleteRequest(BaseModel):
    """删除机器人请求模型"""
    uid: str = Field(..., description="机器人UID")

class RobotAddKnowledgeRequest(BaseModel):
    """绑定知识库请求模型"""
    robot_uid: str = Field(..., description="机器人UID")
    knowledge_uids: List[str] = Field(..., min_items=1, description="知识库UID列表")
    
    @field_validator('knowledge_uids')
    @classmethod
    def validate_knowledge_uids(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError('知识库UID列表不能为空')
        return v

class RobotFilterCreate(BaseModel):
    """创建机器人过滤规则请求模型"""
    robot_uid: str = Field(..., description="机器人UID")
    filter_type: int = Field(..., ge=0, le=2, description="过滤类型：0-黑名单 1-白名单 2-先通过白名单再过滤黑名单")
    is_filter_groups: Optional[bool] = Field(None, description="是否过滤群聊")
    is_filter_private: Optional[bool] = Field(None, description="是否过滤私聊")
    is_filter_members: Optional[bool] = Field(None, description="是否过滤群成员")
    whitelist_content: Optional[List[str]] = Field(None, description="白名单内容")
    blacklist_content: Optional[List[str]] = Field(None, description="黑名单内容")
    whitelist_names: Optional[List[str]] = Field(None, description="白名单名称")
    blacklist_names: Optional[List[str]] = Field(None, description="黑名单名称")
    
    @field_validator('filter_type')
    @classmethod
    def validate_filter_type(cls, v: int) -> int:
        if v not in [0, 1, 2]:
            raise ValueError('过滤类型值无效')
        return v

class RobotFilterUpdate(BaseModel):
    """更新机器人过滤规则请求模型"""
    robot_uid: str = Field(..., description="机器人UID")
    filter_type: Optional[int] = Field(None, ge=0, le=2, description="过滤类型：0-黑名单 1-白名单 2-先通过白名单再过滤黑名单")
    is_filter_groups: Optional[bool] = Field(None, description="是否过滤群聊")
    is_filter_private: Optional[bool] = Field(None, description="是否过滤私聊")
    is_filter_members: Optional[bool] = Field(None, description="是否过滤群成员")
    whitelist_content: Optional[List[str]] = Field(None, description="白名单内容")
    blacklist_content: Optional[List[str]] = Field(None, description="黑名单内容")
    whitelist_names: Optional[List[str]] = Field(None, description="白名单名称")
    blacklist_names: Optional[List[str]] = Field(None, description="黑名单名称")
    
    @field_validator('filter_type')
    @classmethod
    def validate_filter_type(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in [0, 1, 2]:
            raise ValueError('过滤类型值无效')
        return v

class RobotFilterOut(BaseModel):
    """机器人过滤规则输出模型"""
    uid: str
    filter_type: int
    is_filter_groups: Optional[bool]
    is_filter_private: Optional[bool]
    is_filter_members: Optional[bool]
    whitelist_content: Optional[str]
    blacklist_content: Optional[str]
    whitelist_names: Optional[str]
    blacklist_names: Optional[str]
    robot_uid: str
    created_time: datetime
    updated_time: datetime
    
    class Config:
        from_attributes = True

class PaginationParams(BaseModel):
    """分页参数模型"""
    skip: int = Field(0, ge=0, description="跳过记录数")
    limit: int = Field(20, ge=1, le=100, description="返回记录数限制")