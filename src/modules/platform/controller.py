from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
import logging

from crud.platform_bind import (
    create_platform_bind,
    get_platform_bind_by_uid,
    get_platform_binds_by_user,
    get_platform_binds_count_by_user,
    update_platform_bind,
    delete_platform_bind
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
from crud.platform_data import (
    create_platform_data,
    get_platform_data_by_uid,
    get_platform_data_list_by_bind,
    get_platform_data_count_by_bind,
    get_platform_data_list_by_video,
    get_platform_data_count_by_video,
    update_platform_data,
    delete_platform_data
)
from db.platform_video import PlatformVideo
from crud.platform_video import (
    create_platform_video,
    get_platform_video_by_uid,
    get_platform_videos_by_user,
    get_platform_videos_count_by_user,
    get_platform_videos_by_bind,
    get_platform_videos_count_by_bind,
    update_platform_video,
    delete_platform_video,
)

logger = logging.getLogger(__name__)


def create_platform_bind_service(db: Session, bind_data: PlatformBindCreate, current_user_uid: str) -> PlatformBindOut:
    """创建平台绑定服务"""
    try:
        bind = create_platform_bind(
            db=db,
            from_user=current_user_uid,
            type=bind_data.type,
            url=bind_data.url,
            user_name=bind_data.user_name,
            user_desc=bind_data.user_desc,
            avatar=bind_data.avatar
        )
        return PlatformBindOut.model_validate(bind)
    except Exception as e:
        logger.error(f"创建平台绑定失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建平台绑定失败"
        )


def get_platform_bind_service(db: Session, uid: str, current_user_uid: str, is_admin: bool = False) -> PlatformBindOut:
    """获取单个平台绑定服务"""
    try:
        bind = get_platform_bind_by_uid(db, uid)
        if not bind:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台绑定不存在")
        if not is_admin and bind.from_user != current_user_uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问该平台绑定")
        return PlatformBindOut.model_validate(bind)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取平台绑定失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取平台绑定失败"
        )


def get_platform_binds_list_service(db: Session, current_user_uid: str, skip: int, limit: int) -> PlatformBindListResponse:
    """获取当前用户的绑定列表服务"""
    try:
        items = get_platform_binds_by_user(db, current_user_uid, skip, limit)
        total = get_platform_binds_count_by_user(db, current_user_uid)
        return PlatformBindListResponse(
            total=total,
            items=[PlatformBindOut.model_validate(i) for i in items],
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"获取平台绑定列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取平台绑定列表失败"
        )


def update_platform_bind_service(db: Session, edit_data: PlatformBindEdit, current_user_uid: str, is_admin: bool = False) -> PlatformBindOut:
    """更新平台绑定服务"""
    try:
        bind = get_platform_bind_by_uid(db, edit_data.uid)
        if not bind:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台绑定不存在")
        if not is_admin and bind.from_user != current_user_uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限修改该平台绑定")
        updated = update_platform_bind(
            db=db,
            uid=edit_data.uid,
            type=edit_data.type,
            url=edit_data.url,
            user_name=edit_data.user_name,
            user_desc=edit_data.user_desc,
            avatar=edit_data.avatar
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台绑定不存在")
        return PlatformBindOut.model_validate(updated)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新平台绑定失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新平台绑定失败"
        )


def delete_platform_bind_service(db: Session, delete_data: PlatformBindDelete, current_user_uid: str, is_admin: bool = False) -> dict:
    """删除平台绑定服务"""
    try:
        bind = get_platform_bind_by_uid(db, delete_data.uid)
        if not bind:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台绑定不存在")
        if not is_admin and bind.from_user != current_user_uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限删除该平台绑定")
        success = delete_platform_bind(db, delete_data.uid)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台绑定不存在")
        return {"message": "平台绑定删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除平台绑定失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除平台绑定失败"
        )


# ---- PlatformData Services ----

def create_platform_data_service(db: Session, data: PlatformDataCreate, current_user_uid: str) -> PlatformDataOut:
    """创建平台数据服务"""
    try:
        # 仅允许操作自己绑定下的视频
        video = db.query(PlatformVideo).filter(PlatformVideo.uid == data.from_video, PlatformVideo.is_del == 0).first()
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="视频不存在")
        bind = get_platform_bind_by_uid(db, video.from_bind)
        if not bind:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关联的平台绑定不存在")
        if bind.from_user != current_user_uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限为该视频创建数据")
        # 默认当天：若未提供 stat_date，则按当天创建，以保证“同日仅一条”的语义
        from datetime import date as _date
        stat_date = data.stat_date or _date.today()

        created = create_platform_data(
            db=db,
            from_video=data.from_video,
            stat_date=stat_date,
            play=data.play,
            like_count=data.like_count,
            comment_count=data.comment_count,
            share=data.share,
        )
        return PlatformDataOut.model_validate(created)
    except ValueError as e:
        # 参数或业务校验失败（如重复数据）
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建平台数据失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建平台数据失败")


def get_platform_data_service(db: Session, uid: str, current_user_uid: str, is_admin: bool = False) -> PlatformDataOut:
    """获取单个平台数据服务"""
    try:
        data = get_platform_data_by_uid(db, uid)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台数据不存在")
        # 从视频反查绑定以校验权限
        video = db.query(PlatformVideo).filter(PlatformVideo.uid == data.from_video).first()
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关联的视频不存在")
        bind = get_platform_bind_by_uid(db, video.from_bind)
        if not bind:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关联的平台绑定不存在")
        if not is_admin and bind.from_user != current_user_uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问该平台数据")
        return PlatformDataOut.model_validate(data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取平台数据失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取平台数据失败")


def get_platform_data_list_service(db: Session, from_bind: str, current_user_uid: str, skip: int, limit: int) -> PlatformDataListResponse:
    """根据绑定UID获取平台数据列表服务"""
    try:
        bind = get_platform_bind_by_uid(db, from_bind)
        if not bind:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台绑定不存在")
        if bind.from_user != current_user_uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问该绑定的数据")
        items = get_platform_data_list_by_bind(db, from_bind, skip, limit)
        total = get_platform_data_count_by_bind(db, from_bind)
        return PlatformDataListResponse(
            total=total,
            items=[PlatformDataOut.model_validate(i) for i in items],
            skip=skip,
            limit=limit
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取平台数据列表失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取平台数据列表失败")


def get_platform_data_list_by_video_service(
    db: Session,
    from_video: str,
    current_user_uid: str,
    skip: int,
    limit: int,
    start_date: "Optional[_date]" = None,
    end_date: "Optional[_date]" = None,
) -> PlatformDataListResponse:
    """按视频UID查询平台数据列表（可选开始/结束日期）"""
    try:
        # 校验视频存在及归属
        video = db.query(PlatformVideo).filter(PlatformVideo.uid == from_video, PlatformVideo.is_del == 0).first()
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="视频不存在")
        bind = get_platform_bind_by_uid(db, video.from_bind)
        if not bind:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关联的平台绑定不存在")
        if bind.from_user != current_user_uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问该视频的数据")

        items = get_platform_data_list_by_video(db, from_video, start_date, end_date, skip, limit)
        total = get_platform_data_count_by_video(db, from_video, start_date, end_date)
        return PlatformDataListResponse(
            total=total,
            items=[PlatformDataOut.model_validate(i) for i in items],
            skip=skip,
            limit=limit,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"按视频查询平台数据列表失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取平台数据列表失败")


def update_platform_data_service(db: Session, edit: PlatformDataEdit, current_user_uid: str, is_admin: bool = False) -> PlatformDataOut:
    """更新平台数据服务"""
    try:
        data = get_platform_data_by_uid(db, edit.uid)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台数据不存在")
        # 从视频反查绑定以校验权限
        video = db.query(PlatformVideo).filter(PlatformVideo.uid == data.from_video, PlatformVideo.is_del == 0).first()
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关联的视频不存在")
        bind = get_platform_bind_by_uid(db, video.from_bind)
        if not bind:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关联的平台绑定不存在")
        if not is_admin and bind.from_user != current_user_uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限修改该平台数据")
        updated = update_platform_data(
            db=db,
            uid=edit.uid,
            play=edit.play,
            like_count=edit.like_count,
            comment_count=edit.comment_count,
            share=edit.share,
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台数据不存在")
        return PlatformDataOut.model_validate(updated)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新平台数据失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新平台数据失败")


def delete_platform_data_service(db: Session, delete: PlatformDataDelete, current_user_uid: str, is_admin: bool = False) -> dict:
    """删除平台数据服务"""
    try:
        data = get_platform_data_by_uid(db, delete.uid)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台数据不存在")
        # 从视频反查绑定以校验权限
        video = db.query(PlatformVideo).filter(PlatformVideo.uid == data.from_video, PlatformVideo.is_del == 0).first()
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关联的视频不存在")
        bind = get_platform_bind_by_uid(db, video.from_bind)
        if not bind:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关联的平台绑定不存在")
        if not is_admin and bind.from_user != current_user_uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限删除该平台数据")
        success = delete_platform_data(db, delete.uid)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台数据不存在")
        return {"message": "平台数据删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除平台数据失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除平台数据失败")


# ---- PlatformVideo Services ----
def create_platform_video_service(db: Session, data: PlatformVideoCreate, current_user_uid: str) -> PlatformVideoOut:
    """创建平台视频服务"""
    try:
        # 仅允许为自己的绑定创建视频
        bind = get_platform_bind_by_uid(db, data.from_bind)
        if not bind:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台绑定不存在")
        if bind.from_user != current_user_uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限为该绑定创建视频")

        created = create_platform_video(
            db=db,
            from_bind=data.from_bind,
            platform_video_id=data.platform_video_id,
            title=data.title,
            url=data.url,
            publish_time=data.publish_time,
            cover=data.cover,
        )
        return PlatformVideoOut.model_validate(created)
    except ValueError as e:
        # 业务校验失败（如重复 platform_video_id）
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建平台视频失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建平台视频失败")


def update_platform_video_service(db: Session, edit: PlatformVideoEdit, current_user_uid: str, is_admin: bool = False) -> PlatformVideoOut:
    """更新平台视频服务"""
    try:
        video = get_platform_video_by_uid(db, edit.uid)
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台视频不存在")
        bind = get_platform_bind_by_uid(db, video.from_bind)
        if not bind:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关联的平台绑定不存在")
        if not is_admin and bind.from_user != current_user_uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限编辑该平台视频")

        updated = update_platform_video(
            db=db,
            uid=edit.uid,
            title=edit.title,
            url=edit.url,
            publish_time=edit.publish_time,
            cover=edit.cover,
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台视频不存在")
        return PlatformVideoOut.model_validate(updated)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新平台视频失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新平台视频失败")


def delete_platform_video_service(db: Session, delete_data: PlatformVideoDelete, current_user_uid: str, is_admin: bool = False) -> dict:
    """删除平台视频服务"""
    try:
        video = get_platform_video_by_uid(db, delete_data.uid)
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台视频不存在")
        bind = get_platform_bind_by_uid(db, video.from_bind)
        if not bind:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关联的平台绑定不存在")
        if not is_admin and bind.from_user != current_user_uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限删除该平台视频")

        success = delete_platform_video(db, delete_data.uid)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台视频不存在")
        return {"message": "平台视频删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除平台视频失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除平台视频失败")


def get_platform_videos_list_service(db: Session, current_user_uid: str, skip: int, limit: int) -> PlatformVideoListResponse:
    """获取当前用户所有绑定下的平台视频列表"""
    try:
        items = get_platform_videos_by_user(db, current_user_uid, skip, limit)
        total = get_platform_videos_count_by_user(db, current_user_uid)
        return PlatformVideoListResponse(
            total=total,
            items=[PlatformVideoOut.model_validate(i) for i in items],
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        logger.error(f"获取平台视频列表失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取平台视频列表失败")


def get_platform_videos_list_by_bind_service(db: Session, from_bind: str, current_user_uid: str, skip: int, limit: int) -> PlatformVideoListResponse:
    """根据绑定UID获取平台视频列表服务（校验归属）"""
    try:
        bind = get_platform_bind_by_uid(db, from_bind)
        if not bind:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="平台绑定不存在")
        if bind.from_user != current_user_uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问该绑定的视频")
        items = get_platform_videos_by_bind(db, from_bind, skip, limit)
        total = get_platform_videos_count_by_bind(db, from_bind)
        return PlatformVideoListResponse(
            total=total,
            items=[PlatformVideoOut.model_validate(i) for i in items],
            skip=skip,
            limit=limit,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取绑定下平台视频列表失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取平台视频列表失败")