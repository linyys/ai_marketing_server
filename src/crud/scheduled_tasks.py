from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from db.scheduled_tasks import ScheduledTask
from typing import List, Optional
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

def create_scheduled_task(
    db: Session, 
    from_user: str,
    name: str,
    content: str,
    description: str,
    platform: int,
    time_cron: str,
    is_system: int = 0
) -> ScheduledTask:
    """创建定时任务"""
    try:
        task_uid = str(uuid.uuid4())
        
        db_task = ScheduledTask(
            uid=task_uid,
            from_user=from_user,
            name=name,
            content=content,
            description=description,
            platform=platform,
            time_cron=time_cron,
            is_system=is_system
        )
        
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        logger.info(f"定时任务创建成功: {db_task.name} (uid: {db_task.uid})")
        return db_task
    except Exception as e:
        db.rollback()
        logger.error(f"创建定时任务失败: {str(e)}")
        raise

def get_scheduled_task_by_uid(db: Session, uid: str) -> Optional[ScheduledTask]:
    """根据uid获取定时任务"""
    return db.query(ScheduledTask).filter(
        and_(ScheduledTask.uid == uid, ScheduledTask.is_del == 0)
    ).first()

def get_scheduled_tasks_by_user(
    db: Session, 
    from_user: str, 
    skip: int = 0, 
    limit: int = 20
) -> List[ScheduledTask]:
    """根据用户获取定时任务列表"""
    return db.query(ScheduledTask).filter(
        and_(
            ScheduledTask.from_user == from_user,
            ScheduledTask.is_del == 0
        )
    ).offset(skip).limit(limit).all()

def get_all_scheduled_tasks(
    db: Session, 
    skip: int = 0, 
    limit: int = 20
) -> List[ScheduledTask]:
    """获取所有定时任务列表（管理员用）"""
    return db.query(ScheduledTask).filter(
        ScheduledTask.is_del == 0
    ).offset(skip).limit(limit).all()

def get_scheduled_tasks_count_by_user(db: Session, from_user: str) -> int:
    """获取用户定时任务总数"""
    return db.query(ScheduledTask).filter(
        and_(
            ScheduledTask.from_user == from_user,
            ScheduledTask.is_del == 0
        )
    ).count()

def get_all_scheduled_tasks_count(db: Session) -> int:
    """获取所有定时任务总数"""
    return db.query(ScheduledTask).filter(
        ScheduledTask.is_del == 0
    ).count()

def update_scheduled_task(
    db: Session,
    uid: str,
    name: Optional[str] = None,
    content: Optional[str] = None,
    description: Optional[str] = None,
    platform: Optional[int] = None,
    time_cron: Optional[str] = None,
    is_enable: Optional[int] = None
) -> Optional[ScheduledTask]:
    """更新定时任务"""
    try:
        task = get_scheduled_task_by_uid(db, uid)
        if not task:
            return None
        
        if name is not None:
            task.name = name
        if content is not None:
            task.content = content
        if description is not None:
            task.description = description
        if platform is not None:
            task.platform = platform
        if time_cron is not None:
            task.time_cron = time_cron
        if is_enable is not None:
            task.is_enable = is_enable
        
        task.updated_time = datetime.now()
        
        db.commit()
        db.refresh(task)
        
        logger.info(f"定时任务更新成功: {task.name} (uid: {task.uid})")
        return task
    except Exception as e:
        db.rollback()
        logger.error(f"更新定时任务失败: {str(e)}")
        raise

def delete_scheduled_task(db: Session, uid: str) -> bool:
    """删除定时任务（软删除）"""
    try:
        task = get_scheduled_task_by_uid(db, uid)
        if not task:
            return False
        
        task.is_del = 1
        task.updated_time = datetime.now()
        
        db.commit()
        
        logger.info(f"定时任务删除成功: {task.name} (uid: {task.uid})")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"删除定时任务失败: {str(e)}")
        raise

def search_scheduled_tasks(
    db: Session,
    name: Optional[str] = None,
    platform: Optional[int] = None,
    is_enable: Optional[int] = None,
    from_user: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> tuple[List[ScheduledTask], int]:
    """搜索定时任务"""
    query = db.query(ScheduledTask).filter(ScheduledTask.is_del == 0)
    
    if name:
        query = query.filter(ScheduledTask.name.like(f"%{name}%"))
    if platform is not None:
        query = query.filter(ScheduledTask.platform == platform)
    if is_enable is not None:
        query = query.filter(ScheduledTask.is_enable == is_enable)
    if from_user:
        query = query.filter(ScheduledTask.from_user == from_user)
    
    total = query.count()
    tasks = query.offset(skip).limit(limit).all()
    
    return tasks, total

def get_enabled_scheduled_tasks(db: Session) -> List[ScheduledTask]:
    """获取所有启用的定时任务"""
    return db.query(ScheduledTask).filter(
        and_(
            ScheduledTask.is_del == 0,
            ScheduledTask.is_enable == 1
        )
    ).all()