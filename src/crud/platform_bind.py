from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
import logging
import uuid

from db.platform_bind import PlatformBind

logger = logging.getLogger(__name__)


def create_platform_bind(db: Session, from_user: str, type: int, url: str, user_name: Optional[str] = None, user_desc: Optional[str] = None, avatar: Optional[str] = None) -> PlatformBind:
    """创建平台绑定"""
    try:
        bind_uid = str(uuid.uuid4())
        db_bind = PlatformBind(
            uid=bind_uid,
            from_user=from_user,
            type=type,
            url=url,
            user_name=user_name,
            user_desc=user_desc,
            avatar=avatar
        )
        db.add(db_bind)
        db.commit()
        db.refresh(db_bind)
        logger.info(f"平台绑定创建成功: {db_bind.uid}")
        return db_bind
    except Exception as e:
        db.rollback()
        logger.error(f"创建平台绑定失败: {str(e)}")
        raise


def get_platform_bind_by_uid(db: Session, uid: str) -> Optional[PlatformBind]:
    """根据UID获取平台绑定"""
    return db.query(PlatformBind).filter(
        and_(PlatformBind.uid == uid, PlatformBind.is_del == 0)
    ).first()


def get_platform_binds_by_user(db: Session, from_user: str, skip: int = 0, limit: int = 20) -> List[PlatformBind]:
    """获取指定用户的绑定列表"""
    return db.query(PlatformBind).filter(
        and_(PlatformBind.from_user == from_user, PlatformBind.is_del == 0)
    ).offset(skip).limit(limit).all()


def get_platform_binds_count_by_user(db: Session, from_user: str) -> int:
    """获取指定用户绑定总数"""
    return db.query(PlatformBind).filter(
        and_(PlatformBind.from_user == from_user, PlatformBind.is_del == 0)
    ).count()


def update_platform_bind(db: Session, uid: str, type: Optional[int] = None, url: Optional[str] = None, user_name: Optional[str] = None, user_desc: Optional[str] = None, avatar: Optional[str] = None) -> Optional[PlatformBind]:
    """更新平台绑定"""
    try:
        bind = get_platform_bind_by_uid(db, uid)
        if not bind:
            return None
        if type is not None:
            bind.type = type
        if url is not None:
            bind.url = url
        if user_name is not None:
            bind.user_name = user_name
        if user_desc is not None:
            bind.user_desc = user_desc
        if avatar is not None:
            bind.avatar = avatar
        bind.updated_time = datetime.now()
        db.commit()
        db.refresh(bind)
        logger.info(f"平台绑定更新成功: {uid}")
        return bind
    except Exception as e:
        db.rollback()
        logger.error(f"更新平台绑定失败: {str(e)}")
        raise


def delete_platform_bind(db: Session, uid: str) -> bool:
    """删除平台绑定（软删除）"""
    try:
        bind = get_platform_bind_by_uid(db, uid)
        if not bind:
            return False
        bind.is_del = 1
        bind.updated_time = datetime.now()
        db.commit()
        logger.info(f"平台绑定删除成功: {uid}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"删除平台绑定失败: {str(e)}")
        raise