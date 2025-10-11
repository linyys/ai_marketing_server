import logging
from typing import List
from fastapi import APIRouter, HTTPException, status, Query

from modules.douyin.controller import (
    fetch_video_detail_service, fetch_user_videos_service,
    fetch_user_profile_service, fetch_video_comments_service,
    fetch_search_suggestions_service
)
from schemas.douyin import (
    VideoDetailResponse, UserVideosResponse,
    UserProfileResponse, VideoCommentsResponse,
    SearchSuggestion
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/douyin", tags=["抖音"])

def _validate_required_param(param_value: str, param_name: str) -> None:
    """验证必需参数"""
    if not param_value or param_value.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{param_name}不能为空"
        )

@router.get("/video/detail", response_model=VideoDetailResponse, summary="获取单个视频详情")
async def get_video_detail(aweme_id: str = Query(..., description="视频ID")):
    """获取抖音单个视频详情"""
    _validate_required_param(aweme_id, "aweme_id")
    return await fetch_video_detail_service(aweme_id)

@router.get("/user/videos", response_model=UserVideosResponse, summary="获取用户作品列表")
async def get_user_videos(
    sec_user_id: str = Query(..., description="用户ID"),
    max_cursor: int = Query(0, description="分页游标"),
    count: int = Query(20, description="每页数量")
):
    """获取抖音用户作品列表"""
    _validate_required_param(sec_user_id, "sec_user_id")
    return await fetch_user_videos_service(sec_user_id, max_cursor, count)

@router.get("/user/profile", response_model=UserProfileResponse, summary="获取用户信息")
async def get_user_profile(sec_user_id: str = Query(..., description="用户ID")):
    """获取抖音用户信息"""
    _validate_required_param(sec_user_id, "sec_user_id")
    return await fetch_user_profile_service(sec_user_id)

@router.get("/video/comments", response_model=VideoCommentsResponse, summary="获取视频评论")
async def get_video_comments(
    aweme_id: str = Query(..., description="视频ID"),
    cursor: int = Query(0, description="分页游标"),
    count: int = Query(20, description="每页数量")
):
    """获取抖音视频评论数据"""
    _validate_required_param(aweme_id, "aweme_id")
    return await fetch_video_comments_service(aweme_id, cursor, count)

@router.get("/search/suggestions", response_model=List[SearchSuggestion], summary="获取搜索建议")
async def get_search_suggestions(keyword: str = Query(..., description="搜索关键词")):
    """根据关键词获取抖音搜索建议"""
    _validate_required_param(keyword, "keyword")
    return await fetch_search_suggestions_service(keyword)