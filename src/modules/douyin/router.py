import logging
from typing import List
from fastapi import APIRouter, HTTPException, status, Query, Body, Depends
from src.modules.douyin.cookie_service import cookie_manager, UserCookieManager
from src.utils.auth import get_current_user, get_current_admin, get_current_admin_or_user

from src.schemas.douyin import DouyinSearchRequest
from src.modules.douyin.controller import (
    DouyinController,
    fetch_video_detail_service,
    fetch_user_videos_service,
    fetch_user_profile_service,
    fetch_video_comments_service,
    fetch_search_suggestions_service,
    _validate_cookie_update_request
)
from src.schemas.douyin import (
    DouyinSearchRequest,
    VideoDetailResponse,
    UserVideosResponse,
    UserProfileResponse,
    VideoCommentsResponse,
    SearchSuggestion,
    DouyinSearchResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/douyin", tags=["抖音"])
controller = DouyinController()

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

@router.get("/search/video", response_model=DouyinSearchResponse, summary="获取视频信息")
async def search_video(
    keyword: str = Query(..., description="搜索关键词"),
    offset: int = Query(0, ge=0, description="分页偏移量"),
    count: int = Query(16, ge=1, le=50, description="每页数量")
):
    """
    搜索抖音视频
    - **keyword**: 搜索关键词
    - **offset**: 分页偏移量（默认0）
    - **count**: 每页数量（1-50，默认16）
    """
    request = DouyinSearchRequest(keyword=keyword, offset=offset, count=count)
    return await controller.search_videos(request)

@router.post("/update-cookie", summary="更新抖音Cookie")
async def update_douyin_cookie(
    cookie: str = Body(..., embed=True, description="完整的Cookie字符串"),
    target_user_id: str = Query(None, description="管理员可选：指定要更新的用户ID，不指定则更新公共Cookie"),
    current_user = Depends(get_current_admin_or_user)
):
    """
    更新抖音请求使用的Cookie（支持普通用户和管理员）
    
    - **cookie**: 完整的Cookie字符串，必须包含所有必要字段
    - **target_user_id**: 管理员可选参数，指定要更新的用户ID
    """
    try:
        # 验证Cookie有效性
        _validate_cookie_update_request(cookie)
        
        # 检查当前用户类型 - 修复：统一使用getattr访问属性
        is_admin = getattr(current_user, 'is_admin', False)
        # 优先使用uid，其次尝试user_id属性
        user_id = getattr(current_user, 'uid', None) or getattr(current_user, 'user_id', None)
        
        # 处理逻辑分支
        if is_admin:
            # 管理员逻辑
            if target_user_id:
                # 管理员更新特定用户的Cookie
                logger.info(f"管理员{user_id}更新用户{target_user_id}的Cookie")
                user_manager = UserCookieManager(target_user_id)
                return user_manager.update_user_cookie(cookie)
            else:
                # 管理员更新公共Cookie
                logger.info(f"管理员{user_id}更新公共Cookie")
                return cookie_manager.update_cookie(cookie)
        else:
            # 普通用户只能更新自己的Cookie
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户ID无效"
                )
            
            logger.info(f"用户{user_id}更新自己的Cookie")
            user_manager = UserCookieManager(user_id)
            return user_manager.update_user_cookie(cookie)
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"更新Cookie时发生意外错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部服务器错误"
        )

@router.post("/toggle-user-mode", summary="切换用户专属模式")
async def toggle_user_specific_mode(
    enable: bool = Body(..., embed=True),
    current_user = Depends(get_current_admin)  # 仅管理员可操作
):
    """
    切换抖音Cookie的用户专属模式
    
    - **enable**: 是否启用用户专属模式
    - **current_user**: 当前管理员信息
    """
    try:
        logger.info(f"管理员{current_user.username}尝试{'启用' if enable else '禁用'}用户专属模式")
        return cookie_manager.toggle_user_specific_mode(enable)
    except Exception as e:
        logger.error(f"切换用户专属模式失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部服务器错误"
        )

@router.post("/restore-cookie", summary="恢复用户Cookie配置")
async def restore_user_cookie(
    current_user: dict = Depends(get_current_user)
):
    """
    从备份恢复用户专属Cookie配置
    
    - **current_user**: 当前认证用户信息
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户ID无效"
            )
        
        logger.info(f"用户{user_id}请求恢复Cookie配置")
        user_manager = UserCookieManager(user_id)
        return user_manager.restore_from_backup()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"恢复Cookie配置时发生错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部服务器错误"
        )

@router.post("/cleanup-expired-configs", summary="清理过期用户配置")
async def cleanup_expired_configs(
    days: int = Body(30, embed=True, ge=7, le=365),
    current_user = Depends(get_current_admin)  # 仅管理员可操作
):
    """
    清理指定天数未更新的用户配置
    
    - **days**: 保留天数（7-365天，默认30天）
    - **current_user**: 当前管理员信息
    """
    try:
        logger.info(f"管理员{current_user.username}请求清理{days}天前的过期配置")
        return cookie_manager.cleanup_expired_user_configs(days)
    except Exception as e:
        logger.error(f"清理过期配置时发生错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部服务器错误"
        )