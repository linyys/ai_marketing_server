from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


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