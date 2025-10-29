import logging
import threading
from typing import Any, List, Dict
from fastapi import HTTPException, status

from src.schemas.douyin import DouyinSearchRequest, DouyinSearchResponse
from src.modules.douyin.web.web_crawler import DouyinWebCrawler
from schemas.douyin import (
    VideoDetailResponse, UserVideosResponse, 
    UserProfileResponse, VideoCommentsResponse,
    SearchSuggestion
)

logger = logging.getLogger(__name__)

# 创建全局锁确保线程安全
crawler_lock = threading.RLock()
user_crawlers: Dict[str, DouyinWebCrawler] = {}
global_crawler = None

def _initialize_crawler(user_id: str = None) -> DouyinWebCrawler:
    """安全初始化爬虫实例"""
    with crawler_lock:
        if user_id:
            # 用户专属模式
            if user_id not in user_crawlers:
                user_crawlers[user_id] = DouyinWebCrawler(user_id)
                logger.info(f"成功初始化用户{user_id}的抖音爬虫实例")
            return user_crawlers[user_id]
        else:
            # 全局模式
            global global_crawler
            if global_crawler is None:
                global_crawler = DouyinWebCrawler()
                logger.info("成功初始化全局抖音爬虫实例")
            return global_crawler

def _refresh_crawler(user_id: str = None):
    """刷新爬虫实例"""
    with crawler_lock:
        if user_id:
            # 刷新特定用户的爬虫实例
            if user_id in user_crawlers:
                old_crawler = user_crawlers[user_id]
                user_crawlers[user_id] = DouyinWebCrawler(user_id)
                logger.info(f"用户{user_id}的抖音爬虫实例已刷新")
                if hasattr(old_crawler, 'cleanup') and callable(old_crawler.cleanup):
                    old_crawler.cleanup()
        else:
            # 刷新全局爬虫实例
            global global_crawler
            old_crawler = global_crawler
            global_crawler = DouyinWebCrawler()
            logger.info("全局抖音爬虫实例已刷新")
            if hasattr(old_crawler, 'cleanup') and callable(old_crawler.cleanup):
                old_crawler.cleanup()

# 更新全局Cookie时同时刷新所有用户的爬虫实例
def _refresh_all_crawlers():
    """刷新所有爬虫实例"""
    _refresh_crawler()  # 刷新全局实例
    # 刷新所有用户实例
    for user_id in list(user_crawlers.keys()):
        _refresh_crawler(user_id)

# 注册到CookieManager
try:
    from src.modules.douyin.cookie_service import cookie_manager
    cookie_manager.register_update_callback(_refresh_crawler)
    _initialize_crawler()
    logger.info("已注册Cookie更新回调处理器")
except ImportError as e:
    logger.error(f"注册Cookie回调失败: {str(e)}")
    _initialize_crawler()

def _get_active_crawler(user_id: str = None) -> DouyinWebCrawler:
    """获取当前有效爬虫实例（线程安全）"""
    if user_id:
        return _initialize_crawler(user_id)
    else:
        return _initialize_crawler()

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

async def fetch_video_detail_service(aweme_id: str, user_id: str = None) -> VideoDetailResponse:
    """获取视频详情服务"""
    try:
        crawler = _get_active_crawler(user_id)
        logger.info(f"{'用户' + user_id + ' ' if user_id else ''}开始获取视频详情，aweme_id: {aweme_id}")
        result = await crawler.fetch_one_video(aweme_id)
        logger.info(f"{'用户' + user_id + ' ' if user_id else ''}成功获取视频详情")
        return _handle_response(
            result, "获取视频详情成功", "获取视频详情失败，未找到相关数据", VideoDetailResponse
        )
    except Exception as e:
        logger.error(f"{'用户' + user_id + ' ' if user_id else ''}获取视频详情异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取视频详情失败: {str(e)}"
        )

async def fetch_user_videos_service(sec_user_id: str, max_cursor: int, count: int, user_id: str = None) -> UserVideosResponse:
    """获取用户作品列表服务"""
    try:
        crawler = _get_active_crawler(user_id)  # 使用用户专属爬虫或全局爬虫
        logger.info(f"{'用户' + user_id + ' ' if user_id else ''}开始获取用户作品列表，sec_user_id: {sec_user_id}")
        result = await crawler.fetch_user_post_videos(sec_user_id, max_cursor, count)
        logger.info(f"{'用户' + user_id + ' ' if user_id else ''}成功获取用户作品列表，sec_user_id: {sec_user_id}")
        return _handle_response(
            result, "获取用户作品列表成功", "获取用户作品列表失败，未找到相关数据", UserVideosResponse
        )
    except Exception as e:
        logger.error(f"{'用户' + user_id + ' ' if user_id else ''}获取用户作品列表异常，sec_user_id: {sec_user_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户作品列表失败: {str(e)}"
        )

async def fetch_user_profile_service(sec_user_id: str, user_id: str = None) -> UserProfileResponse:
    """获取用户信息服务"""
    try:
        crawler = _get_active_crawler(user_id)  # 使用用户专属爬虫或全局爬虫
        logger.info(f"{'用户' + user_id + ' ' if user_id else ''}开始获取用户信息，sec_user_id: {sec_user_id}")
        result = await crawler.handler_user_profile(sec_user_id)
        logger.info(f"{'用户' + user_id + ' ' if user_id else ''}成功获取用户信息，sec_user_id: {sec_user_id}")
        return _handle_response(
            result, "获取用户信息成功", "获取用户信息失败，未找到相关数据", UserProfileResponse
        )
    except Exception as e:
        logger.error(f"{'用户' + user_id + ' ' if user_id else ''}获取用户信息异常，sec_user_id: {sec_user_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )

async def fetch_video_comments_service(aweme_id: str, cursor: int, count: int, user_id: str = None) -> VideoCommentsResponse:
    """获取视频评论数据服务"""
    try:
        crawler = _get_active_crawler(user_id)  # 使用用户专属爬虫或全局爬虫
        logger.info(f"{'用户' + user_id + ' ' if user_id else ''}开始获取视频评论，aweme_id: {aweme_id}")
        result = await crawler.fetch_video_comments(aweme_id, cursor, count)
        logger.info(f"{'用户' + user_id + ' ' if user_id else ''}成功获取视频评论，aweme_id: {aweme_id}")
        return _handle_response(
            result, "获取视频评论成功", "获取视频评论失败，未找到相关数据", VideoCommentsResponse
        )
    except Exception as e:
        logger.error(f"{'用户' + user_id + ' ' if user_id else ''}获取视频评论异常，aweme_id: {aweme_id}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取视频评论失败: {str(e)}"
        )

async def fetch_search_suggestions_service(keyword: str, user_id: str = None) -> List[SearchSuggestion]:
    """获取搜索建议服务"""
    try:
        crawler = _get_active_crawler(user_id)  # 使用用户专属爬虫或全局爬虫
        logger.info(f"{'用户' + user_id + ' ' if user_id else ''}开始获取搜索建议，关键词: {keyword}")
        suggestions_data = await crawler.get_search_suggestions(keyword)
        suggestions = [SearchSuggestion(content=item['content']) for item in suggestions_data]
        logger.info(f"{'用户' + user_id + ' ' if user_id else ''}成功获取搜索建议，数量: {len(suggestions)}")
        return suggestions
    except Exception as e:
        logger.error(f"{'用户' + user_id + ' ' if user_id else ''}获取搜索建议异常，关键词: {keyword}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取搜索建议失败: {str(e)}"
        )


class DouyinController:
    async def search_videos(self, request: DouyinSearchRequest, user_id: str = None) -> DouyinSearchResponse:
        """处理抖音视频搜索请求"""
        try:
            crawler = _get_active_crawler(user_id)
            result = await crawler.search_videos(
                keyword=request.keyword,
                offset=request.offset,
                count=request.count
            )
            
            # 验证响应结构
            if "data" not in result or "has_more" not in result:
                raise HTTPException(
                    status_code=500,
                    detail="抖音API返回数据结构异常"
                )

            video_items = []
            for item in result.get('data', []):
                if 'aweme_info' in item:
                    video_items.append(self._parse_video_item(item['aweme_info']))

            return DouyinSearchResponse(
                has_more=result.get('has_more', 0),
                cursor=result.get('cursor', 0),
                data=video_items
            )
        except Exception as e:
            logger.error(f"抖音搜索失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"搜索服务异常: {str(e)}"
            )
    
    def _parse_video_item(self, aweme_info: dict) -> dict:
        """解析抖音视频信息"""
        # 提取作者信息
        author = aweme_info.get('author', {})
        author_data = {
            'uid': author.get('uid', ''),
            'nickname': author.get('nickname', ''),
            'avatar': author.get('avatar_thumb', {}).get('url_list', [''])[0] if author.get('avatar_thumb') else ''
        }
        
        # 提取统计信息
        statistics = aweme_info.get('statistics', {})
        stats_data = {
            'digg_count': statistics.get('digg_count', 0),
            'comment_count': statistics.get('comment_count', 0),
            'share_count': statistics.get('share_count', 0)
        }
        
        # 提取视频信息
        video = aweme_info.get('video', {})
        play_addr = video.get('play_addr', {})
        video_data = {
            'url_list': play_addr.get('url_list', []),
            'width': play_addr.get('width', 0),
            'height': play_addr.get('height', 0),
            'duration': video.get('duration', 0)
        }
        
        # 提取封面信息
        cover = video.get('cover', {})
        cover_data = {
            'url_list': cover.get('url_list', []),
            'width': cover.get('width', 0),
            'height': cover.get('height', 0)
        }
        
        # 构建最终的视频数据字典
        return {
            'aweme_id': aweme_info.get('aweme_id', ''),
            'desc': aweme_info.get('desc', ''),
            'author': author_data,
            'statistics': stats_data,
            'video': video_data,
            'cover': cover_data,
            'create_time': aweme_info.get('create_time', 0)
        }

def _validate_cookie_update_request(cookie_str: str):
    """验证Cookie更新请求"""
    if not cookie_str or len(cookie_str) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cookie字符串无效"
        )
    
    # 检查是否包含敏感信息
    sensitive_fields = ['passport_csrf_token', 'passport_mfa_token']
    for field in sensitive_fields:
        if f"{field}=" in cookie_str:
            logger.warning(f"检测到敏感字段: {field}")
            # 不直接拒绝，仅记录警告（符合安全规范）
    
    # 验证必要字段
    required_fields = ['sessionid', 'sid_guard', 'uid_tt']
    for field in required_fields:
        if f"{field}=" not in cookie_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"缺少必要字段: {field}"
            )