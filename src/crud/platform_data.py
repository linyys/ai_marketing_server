from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime, date as _date
import logging
import uuid

from db.platform_data import PlatformData
from db.platform_video import PlatformVideo

logger = logging.getLogger(__name__)


def create_platform_data(
    db: Session,
    from_video: str,
    stat_date: Optional[datetime.date],
    play: int,
    like_count: int,
    comment_count: int,
    share: int,
) -> PlatformData:
    """创建平台数据（按视频+日期）"""
    try:
        # 校验from_video存在且未删除
        video_row = db.query(PlatformVideo).filter(and_(PlatformVideo.uid == from_video, PlatformVideo.is_del == 0)).first()
        if not video_row:
            raise ValueError("视频不存在或已删除")

        # 同视频同日只允许一条（软删不计入）
        if stat_date is not None:
            exists = db.query(PlatformData).filter(
                and_(
                    PlatformData.from_video == from_video,
                    PlatformData.stat_date == stat_date,
                    PlatformData.is_del == 0,
                )
            ).first()
            if exists:
                raise ValueError("该视频在该日期的数据已存在")

        data_uid = str(uuid.uuid4())
        db_data = PlatformData(
            uid=data_uid,
            from_video=from_video,
            stat_date=stat_date,
            play=play or 0,
            like_count=like_count or 0,
            comment_count=comment_count or 0,
            share=share or 0,
        )
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        logger.info(f"平台数据创建成功: {db_data.uid}")
        return db_data
    except Exception as e:
        db.rollback()
        logger.error(f"创建平台数据失败: {str(e)}")
        raise


def get_platform_data_by_uid(db: Session, uid: str) -> Optional[PlatformData]:
    """根据UID获取平台数据"""
    return db.query(PlatformData).filter(
        and_(PlatformData.uid == uid, PlatformData.is_del == 0)
    ).first()


def get_platform_data_list_by_bind(db: Session, from_bind: str, skip: int = 0, limit: int = 20) -> List[PlatformData]:
    """根据绑定UID获取平台数据列表（通过视频表关联）"""
    return (
        db.query(PlatformData)
        .join(PlatformVideo, PlatformData.from_video == PlatformVideo.uid)
        .filter(and_(PlatformVideo.from_bind == from_bind, PlatformVideo.is_del == 0, PlatformData.is_del == 0))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_platform_data_count_by_bind(db: Session, from_bind: str) -> int:
    """根据绑定UID获取平台数据总数（通过视频表关联）"""
    return (
        db.query(PlatformData)
        .join(PlatformVideo, PlatformData.from_video == PlatformVideo.uid)
        .filter(and_(PlatformVideo.from_bind == from_bind, PlatformVideo.is_del == 0, PlatformData.is_del == 0))
        .count()
    )


def get_platform_data_list_by_video(
    db: Session,
    from_video: str,
    start_date: Optional[_date] = None,
    end_date: Optional[_date] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[PlatformData]:
    """根据视频UID与可选时间范围获取平台数据列表"""
    query = db.query(PlatformData).filter(and_(PlatformData.from_video == from_video, PlatformData.is_del == 0))
    if start_date is not None:
        query = query.filter(PlatformData.stat_date >= start_date)
    if end_date is not None:
        query = query.filter(PlatformData.stat_date <= end_date)
    return query.offset(skip).limit(limit).all()


def get_platform_data_count_by_video(
    db: Session,
    from_video: str,
    start_date: Optional[_date] = None,
    end_date: Optional[_date] = None,
) -> int:
    """根据视频UID与可选时间范围获取平台数据总数"""
    query = db.query(PlatformData).filter(and_(PlatformData.from_video == from_video, PlatformData.is_del == 0))
    if start_date is not None:
        query = query.filter(PlatformData.stat_date >= start_date)
    if end_date is not None:
        query = query.filter(PlatformData.stat_date <= end_date)
    return query.count()


def update_platform_data(
    db: Session,
    uid: str,
    play: Optional[int] = None,
    like_count: Optional[int] = None,
    comment_count: Optional[int] = None,
    share: Optional[int] = None,
) -> Optional[PlatformData]:
    """更新平台数据"""
    try:
        data = get_platform_data_by_uid(db, uid)
        if not data:
            return None
        if play is not None:
            data.play = play
        if like_count is not None:
            data.like_count = like_count
        if comment_count is not None:
            data.comment_count = comment_count
        if share is not None:
            data.share = share
        data.updated_time = datetime.now()
        db.commit()
        db.refresh(data)
        logger.info(f"平台数据更新成功: {uid}")
        return data
    except Exception as e:
        db.rollback()
        logger.error(f"更新平台数据失败: {str(e)}")
        raise


def delete_platform_data(db: Session, uid: str) -> bool:
    """删除平台数据（软删除）"""
    try:
        data = get_platform_data_by_uid(db, uid)
        if not data:
            return False
        data.is_del = 1
        data.updated_time = datetime.now()
        db.commit()
        logger.info(f"平台数据删除成功: {uid}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"删除平台数据失败: {str(e)}")
        raise