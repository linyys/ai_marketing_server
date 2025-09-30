from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re

class ScheduledTaskCreate(BaseModel):
    """创建定时任务请求模型"""
    name: str = Field(..., min_length=1, max_length=50, description="任务名称")
    content: str = Field(..., min_length=1, description="任务内容")
    description: str = Field(..., min_length=1, max_length=255, description="任务描述")
    platform: int = Field(..., ge=0, le=2, description="平台：0-抖音，1-微信视频号，2-小红书")
    time_cron: str = Field(..., min_length=1, max_length=255, description="定时任务表达式")
    is_system: Optional[int] = Field(0, ge=0, le=1, description="是否系统级提醒：0-否，1-是")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('任务名称不能为空')
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('任务内容不能为空')
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('任务描述不能为空')
        return v

    @field_validator('time_cron')
    @classmethod
    def validate_time_cron(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('定时任务表达式不能为空')
        # 简单的cron表达式验证（可以根据需要扩展）
        cron_parts = v.split()
        if len(cron_parts) not in [5, 6]:
            raise ValueError('定时任务表达式格式不正确')
        return v

class ScheduledTaskUpdate(BaseModel):
    """更新定时任务请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="任务名称")
    content: Optional[str] = Field(None, min_length=1, description="任务内容")
    description: Optional[str] = Field(None, min_length=1, max_length=255, description="任务描述")
    platform: Optional[int] = Field(None, ge=0, le=2, description="平台：0-抖音，1-微信视频号，2-小红书")
    time_cron: Optional[str] = Field(None, min_length=1, max_length=255, description="定时任务表达式")
    is_enable: Optional[int] = Field(None, ge=0, le=1, description="是否启用：0-否，1-是")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('任务名称不能为空')
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('任务内容不能为空')
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('任务描述不能为空')
        return v

    @field_validator('time_cron')
    @classmethod
    def validate_time_cron(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('定时任务表达式不能为空')
            cron_parts = v.split()
            if len(cron_parts) not in [5, 6]:
                raise ValueError('定时任务表达式格式不正确')
        return v

class ScheduledTaskEdit(BaseModel):
    """编辑定时任务请求模型"""
    uid: str = Field(..., description="任务UID")
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="任务名称")
    content: Optional[str] = Field(None, min_length=1, description="任务内容")
    description: Optional[str] = Field(None, min_length=1, max_length=255, description="任务描述")
    platform: Optional[int] = Field(None, ge=0, le=2, description="平台：0-抖音，1-微信视频号，2-小红书")
    time_cron: Optional[str] = Field(None, min_length=1, max_length=255, description="定时任务表达式")
    is_enable: Optional[int] = Field(None, ge=0, le=1, description="是否启用：0-否，1-是")

class ScheduledTaskDelete(BaseModel):
    """删除定时任务请求模型"""
    uid: str = Field(..., description="任务UID")

class ScheduledTaskOut(BaseModel):
    """定时任务输出模型"""
    id: int
    uid: str
    is_del: int
    created_time: datetime
    updated_time: datetime
    is_enable: int
    from_user: Optional[str]
    name: str
    content: str
    description: str
    platform: int
    time_cron: str
    is_system: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "uid": "550e8400-e29b-41d4-a716-446655440000",
                "is_del": 0,
                "created_time": "2023-01-01T12:00:00",
                "updated_time": "2023-01-01T12:00:00",
                "is_enable": 1,
                "from_user": "user-uid-123",
                "name": "每日抖音发布",
                "content": "发布今日营销内容到抖音平台",
                "description": "自动化抖音内容发布任务",
                "platform": 0,
                "time_cron": "0 9 * * *",
                "is_system": 0
            }
        }

class ScheduledTaskListResponse(BaseModel):
    """定时任务列表响应模型"""
    total: int = Field(..., description="总数量")
    items: List[ScheduledTaskOut] = Field(..., description="定时任务列表")
    skip: int = Field(..., description="跳过数量")
    limit: int = Field(..., description="限制数量")

class ScheduledTaskSearchParams(BaseModel):
    """定时任务搜索参数模型"""
    name: Optional[str] = Field(None, description="任务名称")
    platform: Optional[int] = Field(None, ge=0, le=2, description="平台：0-抖音，1-微信视频号，2-小红书")
    is_enable: Optional[int] = Field(None, ge=0, le=1, description="是否启用：0-否，1-是")

class PlatformEnum:
    """平台枚举"""
    DOUYIN = 0  # 抖音
    WECHAT_VIDEO = 1  # 微信视频号
    XIAOHONGSHU = 2  # 小红书

    @classmethod
    def get_platform_name(cls, platform: int) -> str:
        """获取平台名称"""
        platform_names = {
            cls.DOUYIN: "抖音",
            cls.WECHAT_VIDEO: "微信视频号",
            cls.XIAOHONGSHU: "小红书"
        }
        return platform_names.get(platform, "未知平台")

    @classmethod
    def is_valid_platform(cls, platform: int) -> bool:
        """验证平台是否有效"""
        return platform in [cls.DOUYIN, cls.WECHAT_VIDEO, cls.XIAOHONGSHU]