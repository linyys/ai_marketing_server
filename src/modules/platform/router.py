from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from utils.auth import get_current_admin_or_user, get_current_user
from modules.platform.controller import (
    create_platform_bind_service,
    get_platform_bind_service,
    get_platform_binds_list_service,
    update_platform_bind_service,
    delete_platform_bind_service,
    create_platform_data_service,
    get_platform_data_list_by_video_service,
    update_platform_data_service,
    delete_platform_data_service,
    create_platform_video_service,
    update_platform_video_service,
    delete_platform_video_service,
    get_platform_videos_list_service,
    get_platform_videos_list_by_bind_service,
)
from schemas.platform import (
    PlatformBindCreate,
    PlatformBindEdit,
    PlatformBindDelete,
    PlatformBindOut,
    PlatformBindListResponse,
    PlatformDataCreate,
    PlatformDataEdit,
    PlatformDataDelete,
    PlatformDataOut,
    PlatformDataListResponse,
    PlatformVideoCreate,
    PlatformVideoOut,
    PlatformVideoEdit,
    PlatformVideoDelete,
    PlatformVideoListResponse,
)
from datetime import date as _date
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["平台绑定"], prefix="/platform")


@router.post("/create", response_model=PlatformBindOut, summary="创建平台绑定")
def create_platform_bind(
    bind_data: PlatformBindCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    logger.info(f"用户 {current_user.uid} 创建平台绑定")
    return create_platform_bind_service(db, bind_data, current_user.uid)


@router.post("/delete", summary="删除平台绑定")
def delete_platform_bind(
    delete_data: PlatformBindDelete,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    logger.info(f"用户 {current_user.uid} 删除平台绑定: {delete_data.uid}")
    return delete_platform_bind_service(db, delete_data, current_user.uid, is_admin)


@router.get("/get/list", response_model=PlatformBindListResponse, summary="查询本人所有平台绑定")
def get_platform_bind_list(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    logger.info(f"用户 {current_user.uid} 获取平台绑定列表")
    return get_platform_binds_list_service(db, current_user.uid, skip, limit)


@router.get("/get/{uid}", response_model=PlatformBindOut, summary="查询指定UID的平台绑定")
def get_platform_bind(
    uid: str = Path(..., description="平台绑定UID"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    logger.info(f"用户 {current_user.uid} 查询平台绑定: {uid}")
    return get_platform_bind_service(db, uid, current_user.uid, is_admin)


@router.post("/edit", response_model=PlatformBindOut, summary="编辑平台绑定")
def edit_platform_bind(
    edit_data: PlatformBindEdit,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    logger.info(f"用户 {current_user.uid} 编辑平台绑定: {edit_data.uid}")
    return update_platform_bind_service(db, edit_data, current_user.uid, is_admin)


# ---- PlatformData Routes ----
@router.post("/data/create", response_model=PlatformDataOut, summary="创建平台数据")
def create_platform_data(
    data: PlatformDataCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    logger.info(f"用户 {current_user.uid} 创建平台数据 for video {data.from_video}")
    return create_platform_data_service(db, data, current_user.uid)


# ---- PlatformVideo Routes ----
@router.post("/video/create", response_model=PlatformVideoOut, summary="添加平台视频")
def create_platform_video(
    data: PlatformVideoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    logger.info(f"用户 {current_user.uid} 添加平台视频 under bind {data.from_bind}")
    return create_platform_video_service(db, data, current_user.uid)


@router.post("/video/edit", response_model=PlatformVideoOut, summary="编辑平台视频")
def edit_platform_video(
    edit_data: PlatformVideoEdit,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    logger.info(f"用户 {current_user.uid} 编辑平台视频: {edit_data.uid}")
    return update_platform_video_service(db, edit_data, current_user.uid, is_admin)


@router.post("/video/delete", summary="删除平台视频")
def delete_platform_video(
    delete_data: PlatformVideoDelete,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    logger.info(f"用户 {current_user.uid} 删除平台视频: {delete_data.uid}")
    return delete_platform_video_service(db, delete_data, current_user.uid, is_admin)


@router.get("/video/get/list", response_model=PlatformVideoListResponse, summary="查询本人所有平台视频")
def get_platform_video_list(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    logger.info(f"用户 {current_user.uid} 获取平台视频列表")
    return get_platform_videos_list_service(db, current_user.uid, skip, limit)


@router.get("/video/get/list/{from_bind}", response_model=PlatformVideoListResponse, summary="查询指定绑定下的平台视频")
def get_platform_video_list_by_bind(
    from_bind: str = Path(..., description="平台绑定UID"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    logger.info(f"用户 {current_user.uid} 获取绑定 {from_bind} 下的平台视频列表")
    return get_platform_videos_list_by_bind_service(db, from_bind, current_user.uid, skip, limit)


@router.get("/data/get/list/by_video/{from_video}", response_model=PlatformDataListResponse, summary="按视频ID查询平台数据列表")
def get_platform_data_list_by_video(
    from_video: str = Path(..., description="平台视频UID"),
    start_date: _date | None = Query(None, description="开始日期，包含边界"),
    end_date: _date | None = Query(None, description="结束日期，包含边界"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    logger.info(
        f"用户 {current_user.uid} 获取平台数据列表 by video {from_video}, start={start_date}, end={end_date}, skip={skip}, limit={limit}"
    )
    try:
        return get_platform_data_list_by_video_service(
            db,
            from_video,
            current_user.uid,
            skip,
            limit,
            start_date,
            end_date,
        )
    except HTTPException as e:
        # 如果未查询到（例如视频尚无数据），返回空数组而非 404
        if e.status_code == 404:
            logger.info(
                f"视频 {from_video} 的平台数据未找到，返回空列表 (skip={skip}, limit={limit})"
            )
            return PlatformDataListResponse(total=0, items=[], skip=skip, limit=limit)
        # 其他错误（如权限问题）仍按原样抛出
        raise


@router.post("/data/edit", response_model=PlatformDataOut, summary="编辑平台数据")
def edit_platform_data(
    edit_data: PlatformDataEdit,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    logger.info(f"用户 {current_user.uid} 编辑平台数据: {edit_data.uid}")
    return update_platform_data_service(db, edit_data, current_user.uid, is_admin)


@router.post("/data/delete", summary="删除平台数据")
def delete_platform_data(
    delete_data: PlatformDataDelete,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    logger.info(f"用户 {current_user.uid} 删除平台数据: {delete_data.uid}")
    return delete_platform_data_service(db, delete_data, current_user.uid, is_admin)