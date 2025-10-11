import logging
from typing import Any, List
from fastapi import HTTPException, status

from modules.douyin.web.web_crawler import DouyinWebCrawler
from schemas.douyin import (
    VideoDetailResponse, UserVideosResponse, 
    UserProfileResponse, VideoCommentsResponse,
    SearchSuggestion
)

logger = logging.getLogger(__name__)

# 创建全局爬虫实例
_crawler = DouyinWebCrawler()

def _handle_response(result: Any, success_msg: str, error_msg: str, response_class):
    """统一处理响应结果"""
    if result:
        return response_class(
            success=True,
            data=result,
            message=success_msg
        )
    else:
        return response_class(
            success=False,
            data=None,
            message=error_msg
        )

async def fetch_video_detail_service(aweme_id: str) -> VideoDetailResponse:
    """获取单个视频详情服务"""
    try:
        logger.info(f"开始获取视频详情，aweme_id: {aweme_id}")
        result = await _crawler.fetch_one_video(aweme_id)
        logger.info(f"成功获取视频详情，aweme_id: {aweme_id}")
        return _handle_response(
            result, "获取视频详情成功", "获取视频详情失败，未找到相关数据", VideoDetailResponse
        )
    except Exception as e:
        logger.error(f"获取视频详情异常，aweme_id: {aweme_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取视频详情失败: {str(e)}"
        )

async def fetch_user_videos_service(sec_user_id: str, max_cursor: int, count: int) -> UserVideosResponse:
    """获取用户作品列表服务"""
    try:
        logger.info(f"开始获取用户作品列表，sec_user_id: {sec_user_id}")
        result = await _crawler.fetch_user_post_videos(sec_user_id, max_cursor, count)
        logger.info(f"成功获取用户作品列表，sec_user_id: {sec_user_id}")
        return _handle_response(
            result, "获取用户作品列表成功", "获取用户作品列表失败，未找到相关数据", UserVideosResponse
        )
    except Exception as e:
        logger.error(f"获取用户作品列表异常，sec_user_id: {sec_user_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户作品列表失败: {str(e)}"
        )

async def fetch_user_profile_service(sec_user_id: str) -> UserProfileResponse:
    """获取用户信息服务"""
    try:
        logger.info(f"开始获取用户信息，sec_user_id: {sec_user_id}")
        result = await _crawler.handler_user_profile(sec_user_id)
        logger.info(f"成功获取用户信息，sec_user_id: {sec_user_id}")
        return _handle_response(
            result, "获取用户信息成功", "获取用户信息失败，未找到相关数据", UserProfileResponse
        )
    except Exception as e:
        logger.error(f"获取用户信息异常，sec_user_id: {sec_user_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )

async def fetch_video_comments_service(aweme_id: str, cursor: int, count: int) -> VideoCommentsResponse:
    """获取视频评论数据服务"""
    try:
        logger.info(f"开始获取视频评论，aweme_id: {aweme_id}")
        result = await _crawler.fetch_video_comments(aweme_id, cursor, count)
        logger.info(f"成功获取视频评论，aweme_id: {aweme_id}")
        return _handle_response(
            result, "获取视频评论成功", "获取视频评论失败，未找到相关数据", VideoCommentsResponse
        )
    except Exception as e:
        logger.error(f"获取视频评论异常，aweme_id: {aweme_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取视频评论失败: {str(e)}"
        )

async def fetch_search_suggestions_service(keyword: str) -> List[SearchSuggestion]:
    """获取搜索建议服务"""
    try:
        logger.info(f"开始获取搜索建议，关键词: {keyword}")
        suggestions_data = await _crawler.get_search_suggestions(keyword)
        suggestions = [SearchSuggestion(content=item['content']) for item in suggestions_data]
        logger.info(f"成功获取搜索建议，数量: {len(suggestions)}")
        return suggestions
    except Exception as e:
        logger.error(f"获取搜索建议异常，关键词: {keyword}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取搜索建议失败: {str(e)}"
        )