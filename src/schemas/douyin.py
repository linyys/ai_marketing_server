from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class Author(BaseModel):
    uid: str
    nickname: str
    avatar: str


class Statistics(BaseModel):
    digg_count: int
    comment_count: int
    share_count: int


class VideoCover(BaseModel):
    url_list: List[str]
    width: int
    height: int


class PlayAddr(BaseModel):
    url_list: List[str]
    width: int
    height: int
    duration: int


class VideoItem(BaseModel):
    aweme_id: str
    desc: str
    author: Author
    statistics: Statistics
    video: PlayAddr
    cover: VideoCover
    create_time: int


class AwemeData(BaseModel):
    type: int
    aweme_info: VideoItem

class DouyinSearchResponse(BaseModel):
    has_more: int
    cursor: int
    data: List[AwemeData]


class VideoDetailRequest(BaseModel):
    """获取单个视频详情请求模型"""
    aweme_id: str = Field(..., description="视频ID")

class VideoDetailResponse(BaseModel):
    """获取单个视频详情响应模型"""
    success: bool = Field(..., description="请求是否成功")
    data: Optional[Dict[str, Any]] = Field(None, description="视频详情数据")
    message: str = Field(..., description="响应消息")

class UserVideosRequest(BaseModel):
    """获取用户作品列表请求模型"""
    sec_user_id: str = Field(..., description="用户安全ID")
    max_cursor: int = Field(0, description="分页游标")
    count: int = Field(10, ge=1, le=50, description="获取数量，最大50")

class UserVideosResponse(BaseModel):
    """获取用户作品列表响应模型"""
    success: bool = Field(..., description="请求是否成功")
    data: Optional[Dict[str, Any]] = Field(None, description="用户作品数据")
    message: str = Field(..., description="响应消息")

class UserProfileRequest(BaseModel):
    """获取用户信息请求模型"""
    sec_user_id: str = Field(..., description="用户安全ID")

class UserProfileResponse(BaseModel):
    """获取用户信息响应模型"""
    success: bool = Field(..., description="请求是否成功")
    data: Optional[Dict[str, Any]] = Field(None, description="用户信息数据")
    message: str = Field(..., description="响应消息")

class VideoCommentsRequest(BaseModel):
    """获取视频评论数据请求模型"""
    aweme_id: str = Field(..., description="视频ID")
    cursor: int = Field(0, description="分页游标")
    count: int = Field(20, ge=1, le=50, description="获取数量，最大50")

class VideoCommentsResponse(BaseModel):
    """获取视频评论数据响应模型"""
    success: bool = Field(..., description="请求是否成功")
    data: Optional[Dict[str, Any]] = Field(None, description="评论数据")
    message: str = Field(..., description="响应消息")

class DouyinErrorResponse(BaseModel):
    """抖音API错误响应模型"""
    success: bool = Field(False, description="请求是否成功")
    error_code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    detail: Optional[str] = Field(None, description="错误详情")

class SearchSuggestion(BaseModel):
    """搜索建议项模型"""
    content: str = Field(..., description="推荐的关键词内容")


class DouyinSearchRequest(BaseModel):
    """抖音视频搜索请求模型"""
    keyword: str = Field(..., description="搜索关键词")
    offset: int = Field(0, ge=0, description="分页偏移量")
    count: int = Field(16, ge=1, le=50, description="每页数量")


class DouyinSearchResponse(BaseModel):
    """抖音视频搜索响应模型"""
    has_more: int = Field(..., description="是否有更多数据")
    cursor: int = Field(..., description="下一页游标")
    data: List[Dict] = Field(..., description="视频列表数据")
