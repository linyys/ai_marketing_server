from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date


class PlatformBindCreate(BaseModel):
    type: int = Field(..., ge=0, le=1, description="类型：0-小红书，1-抖音")
    url: str = Field(..., min_length=1, max_length=255, description="绑定的URL")
    user_name: str = Field(..., min_length=1, max_length=255, description="绑定平台的用户名")
    user_desc: str = Field(..., min_length=1, max_length=255, description="绑定平台的用户简介")
    avatar: str = Field(..., min_length=1, max_length=255, description="绑定平台的用户头像")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("绑定的URL不能为空")
        return v

    @field_validator("user_name")
    @classmethod
    def validate_user_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("绑定平台的用户名不能为空")
        return v

    @field_validator("user_desc")
    @classmethod
    def validate_user_desc(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("绑定平台的用户简介不能为空")
        return v

    @field_validator("avatar")
    @classmethod
    def validate_avatar(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("绑定平台的用户头像不能为空")
        return v


class PlatformBindEdit(BaseModel):
    uid: str = Field(..., description="绑定UID")
    type: Optional[int] = Field(None, ge=0, le=1, description="类型：0-小红书，1-抖音")
    url: Optional[str] = Field(None, min_length=1, max_length=255, description="绑定的URL")
    user_name: Optional[str] = Field(None, min_length=1, max_length=255, description="绑定平台的用户名")
    user_desc: Optional[str] = Field(None, min_length=1, max_length=255, description="绑定平台的用户简介")
    avatar: Optional[str] = Field(None, min_length=1, max_length=255, description="绑定平台的用户头像")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("绑定的URL不能为空")
        return v

    @field_validator("user_name")
    @classmethod
    def validate_user_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("绑定平台的用户名不能为空")
        return v

    @field_validator("user_desc")
    @classmethod
    def validate_user_desc(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("绑定平台的用户简介不能为空")
        return v

    @field_validator("avatar")
    @classmethod
    def validate_avatar(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("绑定平台的用户头像不能为空")
        return v


class PlatformBindDelete(BaseModel):
    uid: str = Field(..., description="绑定UID")


class PlatformBindOut(BaseModel):
    id: int
    uid: str
    is_del: int
    created_time: datetime
    updated_time: datetime
    from_user: str
    type: int
    url: str
    user_name: Optional[str]
    user_desc: Optional[str]
    avatar: Optional[str]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "uid": "550e8400-e29b-41d4-a716-446655440000",
                "is_del": 0,
                "created_time": "2023-01-01T12:00:00",
                "updated_time": "2023-01-01T12:00:00",
                "from_user": "user-uid-123",
                "type": 1,
                "url": "https://www.douyin.com/user/xxx",
                "user_name": "抖音用户A",
                "user_desc": "美食博主",
                "avatar": "https://example.com/avatar.jpg"
            }
        }


class PlatformBindListResponse(BaseModel):
    total: int = Field(..., description="总数量")
    items: List[PlatformBindOut] = Field(..., description="绑定列表")
    skip: int = Field(..., description="跳过数量")
    limit: int = Field(..., description="限制数量")


# ---- PlatformVideo Schemas ----
class PlatformVideoCreate(BaseModel):
    from_bind: str = Field(..., description="对应 platform_bind 的UID")
    platform_video_id: str = Field(..., min_length=1, max_length=255, description="平台侧视频ID")
    title: Optional[str] = Field(None, max_length=255, description="视频标题")
    url: Optional[str] = Field(None, description="视频URL（LONGTEXT）")
    publish_time: Optional[int] = Field(None, ge=0, description="视频发布时间时间戳(秒)")
    cover: Optional[str] = Field(None, description="封面URL（LONGTEXT）")

    @field_validator("platform_video_id")
    @classmethod
    def validate_platform_video_id(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("平台侧视频ID不能为空")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
        return v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
        return v

    @field_validator("cover")
    @classmethod
    def validate_cover(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
        return v


class PlatformVideoOut(BaseModel):
    id: int
    uid: str
    is_del: int
    created_time: datetime
    updated_time: datetime
    from_bind: str
    platform_video_id: str
    title: Optional[str]
    url: Optional[str]
    publish_time: Optional[int]
    cover: Optional[str]

    class Config:
        from_attributes = True


class PlatformVideoEdit(BaseModel):
    uid: str = Field(..., description="平台视频UID")
    title: Optional[str] = Field(None, max_length=255, description="视频标题")
    url: Optional[str] = Field(None, description="视频URL（LONGTEXT）")
    publish_time: Optional[int] = Field(None, ge=0, description="视频发布时间时间戳(秒)")
    cover: Optional[str] = Field(None, description="封面URL（LONGTEXT）")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
        return v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
        return v

    @field_validator("cover")
    @classmethod
    def validate_cover(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
        return v


class PlatformVideoDelete(BaseModel):
    uid: str = Field(..., description="平台视频UID")


class PlatformVideoListResponse(BaseModel):
    total: int = Field(..., description="总数量")
    items: List[PlatformVideoOut] = Field(..., description="视频列表")
    skip: int = Field(..., description="跳过数量")
    limit: int = Field(..., description="限制数量")


# ---- PlatformData Schemas ----
class PlatformDataCreate(BaseModel):
    from_video: str = Field(..., description="对应platform_video的UID")
    stat_date: Optional[date] = Field(None, description="统计日期（每日一条）")
    play: int = Field(0, ge=0, description="播放量")
    like_count: int = Field(0, ge=0, description="点赞数量")
    comment_count: int = Field(0, ge=0, description="评论数量")
    share: int = Field(0, ge=0, description="分享数量")
    # 移除 video 字段（数据库已删除该列）


class PlatformDataEdit(BaseModel):
    uid: str = Field(..., description="平台数据UID")
    play: Optional[int] = Field(None, ge=0, description="播放量")
    like_count: Optional[int] = Field(None, ge=0, description="点赞数量")
    comment_count: Optional[int] = Field(None, ge=0, description="评论数量")
    share: Optional[int] = Field(None, ge=0, description="分享数量")
    # 移除 video 字段（数据库已删除该列）


class PlatformDataDelete(BaseModel):
    uid: str = Field(..., description="平台数据UID")


class PlatformDataOut(BaseModel):
    id: int
    uid: str
    is_del: int
    created_time: datetime
    updated_time: datetime
    from_video: Optional[str]
    stat_date: Optional[date]
    play: int
    like_count: int
    comment_count: int
    share: int

    class Config:
        from_attributes = True


class PlatformDataListResponse(BaseModel):
    total: int = Field(..., description="总数量")
    items: List[PlatformDataOut] = Field(..., description="数据列表")
    skip: int = Field(..., description="跳过数量")
    limit: int = Field(..., description="限制数量")