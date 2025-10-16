from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime
import logging
import uuid

from db.platform_video import PlatformVideo
from db.platform_bind import PlatformBind

logger = logging.getLogger(__name__)


def create_platform_video(
    db: Session,
    from_bind: str,
    platform_video_id: str,
    title: Optional[str] = None,
    url: Optional[str] = None,
    publish_time: Optional[int] = None,
    cover: Optional[str] = None,
) -> PlatformVideo:
    """创建平台视频（绑定下的单个视频记录）"""
    try:
        # 校验绑定存在且未删除
        bind_row = db.query(PlatformBind).filter(and_(PlatformBind.uid == from_bind, PlatformBind.is_del == 0)).first()
        if not bind_row:
            raise ValueError("平台绑定不存在或已删除")

        # 防止同一绑定下重复的视频ID
        exists = db.query(PlatformVideo).filter(
            and_(
                PlatformVideo.from_bind == from_bind,
                PlatformVideo.platform_video_id == platform_video_id,
                PlatformVideo.is_del == 0,
            )
        ).first()
        if exists:
            raise ValueError("同一绑定下该平台视频ID已存在")

        video_uid = str(uuid.uuid4())
        db_video = PlatformVideo(
            uid=video_uid,
            from_bind=from_bind,
            platform_video_id=platform_video_id,
            title=title,
            url=url,
            publish_time=publish_time,
            cover=cover,
        )
        db.add(db_video)
        db.commit()
        db.refresh(db_video)
        logger.info(f"平台视频创建成功: {db_video.uid}")
        return db_video
    except Exception as e:
        db.rollback()
        logger.error(f"创建平台视频失败: {str(e)}")
        raise


def get_platform_video_by_uid(db: Session, uid: str) -> Optional[PlatformVideo]:
    """根据UID获取平台视频（未删除）"""
    return db.query(PlatformVideo).filter(and_(PlatformVideo.uid == uid, PlatformVideo.is_del == 0)).first()


def get_platform_videos_by_user(db: Session, user_uid: str, skip: int = 0, limit: int = 20) -> List[PlatformVideo]:
    """获取当前用户所有绑定下的视频列表"""
    from db.platform_bind import PlatformBind as _Bind
    return (
        db.query(PlatformVideo)
        .join(_Bind, PlatformVideo.from_bind == _Bind.uid)
        .filter(and_(
            _Bind.from_user == user_uid,
            _Bind.is_del == 0,
            PlatformVideo.is_del == 0,
        ))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_platform_videos_count_by_user(db: Session, user_uid: str) -> int:
    """获取当前用户所有绑定下的视频总数"""
    from db.platform_bind import PlatformBind as _Bind
    return (
        db.query(PlatformVideo)
        .join(_Bind, PlatformVideo.from_bind == _Bind.uid)
        .filter(and_(
            _Bind.from_user == user_uid,
            _Bind.is_del == 0,
            PlatformVideo.is_del == 0,
        ))
        .count()
    )


def get_platform_videos_by_bind(db: Session, from_bind: str, skip: int = 0, limit: int = 20) -> List[PlatformVideo]:
    """根据绑定UID获取平台视频列表"""
    return (
        db.query(PlatformVideo)
        .filter(and_(PlatformVideo.from_bind == from_bind, PlatformVideo.is_del == 0))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_platform_videos_count_by_bind(db: Session, from_bind: str) -> int:
    """根据绑定UID获取平台视频总数"""
    return (
        db.query(PlatformVideo)
        .filter(and_(PlatformVideo.from_bind == from_bind, PlatformVideo.is_del == 0))
        .count()
    )


def update_platform_video(
    db: Session,
    uid: str,
    title: Optional[str] = None,
    url: Optional[str] = None,
    publish_time: Optional[int] = None,
    cover: Optional[str] = None,
) -> Optional[PlatformVideo]:
    """更新平台视频（不允许修改绑定与平台视频ID）"""
    try:
        video = get_platform_video_by_uid(db, uid)
        if not video:
            return None
        if title is not None:
            video.title = title
        if url is not None:
            video.url = url
        if publish_time is not None:
            video.publish_time = publish_time
        if cover is not None:
            video.cover = cover
        video.updated_time = datetime.now()
        db.commit()
        db.refresh(video)
        logger.info(f"平台视频更新成功: {uid}")
        return video
    except Exception as e:
        db.rollback()
        logger.error(f"更新平台视频失败: {str(e)}")
        raise


def delete_platform_video(db: Session, uid: str) -> bool:
    """删除平台视频（软删除）"""
    try:
        video = get_platform_video_by_uid(db, uid)
        if not video:
            return False
        video.is_del = 1
        video.updated_time = datetime.now()
        db.commit()
        logger.info(f"平台视频删除成功: {uid}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"删除平台视频失败: {str(e)}")
        raise