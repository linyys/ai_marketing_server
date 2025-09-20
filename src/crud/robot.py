from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from db.robots import Robots
from db.robot_filters import RobotFilters
from db.robots_knowledges_relations import RobotsKnowledgesRelations
from typing import List, Optional, Tuple
from datetime import datetime
import logging
import uuid
import json

logger = logging.getLogger(__name__)

def create_robot(db: Session, name: str, reply_type: int, platform: int, login_type: int, 
                description: str, from_user_uid: str, account: Optional[str] = None, 
                password: Optional[str] = None) -> Robots:
    """创建机器人"""
    try:
        db_robot = Robots(
            uid=str(uuid.uuid4()),
            name=name,
            reply_type=reply_type,
            account=account,
            password=password,
            platform=platform,
            login_type=login_type,
            description=description,
            from_user_uid=from_user_uid,
            is_del=0,
            is_enable=0,
            is_bind_knowledges=0,
            is_bind_filter=0
        )
        db.add(db_robot)
        db.commit()
        db.refresh(db_robot)
        logger.info(f"机器人创建成功: {db_robot.uid}")
        return db_robot
    except Exception as e:
        db.rollback()
        logger.error(f"创建机器人失败: {str(e)}")
        raise ValueError(f"创建机器人失败: {str(e)}")

def get_robot_by_uid(db: Session, uid: str) -> Optional[Robots]:
    """根据UID获取机器人"""
    return db.query(Robots).filter(and_(Robots.uid == uid, Robots.is_del == 0)).first()

def get_robots(db: Session, skip: int = 0, limit: int = 20) -> List[Robots]:
    """获取所有机器人列表（管理员用）"""
    return db.query(Robots).filter(Robots.is_del == 0).offset(skip).limit(limit).all()

def get_robots_count(db: Session) -> int:
    """获取机器人总数（管理员用）"""
    return db.query(Robots).filter(Robots.is_del == 0).count()

def get_robots_by_user(db: Session, user_uid: str, skip: int = 0, limit: int = 20) -> List[Robots]:
    """获取指定用户的机器人列表"""
    return db.query(Robots).filter(
        and_(Robots.from_user_uid == user_uid, Robots.is_del == 0)
    ).offset(skip).limit(limit).all()

def get_robots_by_user_count(db: Session, user_uid: str) -> int:
    """获取指定用户的机器人总数"""
    return db.query(Robots).filter(
        and_(Robots.from_user_uid == user_uid, Robots.is_del == 0)
    ).count()

def update_robot(db: Session, robot_uid: str, name: Optional[str] = None, 
                reply_type: Optional[int] = None, account: Optional[str] = None,
                password: Optional[str] = None, platform: Optional[int] = None,
                login_type: Optional[int] = None, description: Optional[str] = None,
                is_enable: Optional[bool] = None) -> Optional[Robots]:
    """更新机器人"""
    try:
        robot = get_robot_by_uid(db, robot_uid)
        if not robot:
            return None
        
        if name is not None:
            robot.name = name
        if reply_type is not None:
            robot.reply_type = reply_type
        if account is not None:
            robot.account = account
        if password is not None:
            robot.password = password
        if platform is not None:
            robot.platform = platform
        if login_type is not None:
            robot.login_type = login_type
        if description is not None:
            robot.description = description
        if is_enable is not None:
            robot.is_enable = 1 if is_enable else 0
        
        db.commit()
        db.refresh(robot)
        logger.info(f"机器人更新成功: {robot_uid}")
        return robot
    except Exception as e:
        db.rollback()
        logger.error(f"更新机器人失败: {robot_uid}, 错误: {str(e)}")
        raise ValueError(f"更新机器人失败: {str(e)}")

def delete_robot(db: Session, robot_uid: str) -> bool:
    """删除机器人（软删除）"""
    try:
        robot = get_robot_by_uid(db, robot_uid)
        if not robot:
            return False
        
        robot.is_del = 1
        db.commit()
        logger.info(f"机器人删除成功: {robot_uid}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"删除机器人失败: {robot_uid}, 错误: {str(e)}")
        raise ValueError(f"删除机器人失败: {str(e)}")

def search_robots(db: Session, name: Optional[str] = None, platform: Optional[int] = None,
                 is_enable: Optional[bool] = None, from_user_uid: Optional[str] = None,
                 start_time: Optional[datetime] = None, end_time: Optional[datetime] = None,
                 skip: int = 0, limit: int = 20) -> Tuple[List[Robots], int]:
    """搜索机器人（管理员用）"""
    query = db.query(Robots).filter(Robots.is_del == 0)
    
    if name:
        query = query.filter(Robots.name.like(f"%{name}%"))
    if platform is not None:
        query = query.filter(Robots.platform == platform)
    if is_enable is not None:
        query = query.filter(Robots.is_enable == (1 if is_enable else 0))
    if from_user_uid:
        query = query.filter(Robots.from_user_uid == from_user_uid)
    if start_time:
        query = query.filter(Robots.created_time >= start_time)
    if end_time:
        query = query.filter(Robots.created_time <= end_time)
    
    total = query.count()
    robots = query.offset(skip).limit(limit).all()
    
    return robots, total

def search_user_robots(db: Session, user_uid: str, name: Optional[str] = None, 
                      platform: Optional[int] = None, is_enable: Optional[bool] = None,
                      start_time: Optional[datetime] = None, end_time: Optional[datetime] = None,
                      skip: int = 0, limit: int = 20) -> Tuple[List[Robots], int]:
    """搜索用户的机器人"""
    query = db.query(Robots).filter(
        and_(Robots.from_user_uid == user_uid, Robots.is_del == 0)
    )
    
    if name:
        query = query.filter(Robots.name.like(f"%{name}%"))
    if platform is not None:
        query = query.filter(Robots.platform == platform)
    if is_enable is not None:
        query = query.filter(Robots.is_enable == (1 if is_enable else 0))
    if start_time:
        query = query.filter(Robots.created_time >= start_time)
    if end_time:
        query = query.filter(Robots.created_time <= end_time)
    
    total = query.count()
    robots = query.offset(skip).limit(limit).all()
    
    return robots, total

def check_robot_permission(db: Session, robot_uid: str, user_uid: str) -> Tuple[bool, Optional[Robots]]:
    """检查用户对机器人的权限"""
    robot = get_robot_by_uid(db, robot_uid)
    if not robot:
        return False, None
    
    # 检查是否为机器人所有者
    if robot.from_user_uid == user_uid:
        return True, robot
    
    return False, robot

def add_robot_knowledges(db: Session, robot_uid: str, knowledge_uids: List[str]) -> bool:
    """为机器人绑定知识库"""
    try:
        # 检查机器人是否存在
        robot = get_robot_by_uid(db, robot_uid)
        if not robot:
            raise ValueError("机器人不存在")
        
        # 先物理删除所有现有的关联关系
        existing_relations = db.query(RobotsKnowledgesRelations).filter(
            and_(
                RobotsKnowledgesRelations.robot_uid == robot_uid,
                RobotsKnowledgesRelations.is_del == 0
            )
        ).all()
        
        for relation in existing_relations:
            db.delete(relation)
        
        # 提交删除操作
        db.commit()
        
        # 批量创建新的关联关系
        for knowledge_uid in knowledge_uids:
            relation = RobotsKnowledgesRelations(
                robot_uid=robot_uid,
                knowledge_uid=knowledge_uid,
                is_del=0
            )
            db.add(relation)
        
        # 更新机器人的绑定知识库状态
        robot.is_bind_knowledges = 1 if knowledge_uids else 0
        
        db.commit()
        logger.info(f"机器人 {robot_uid} 绑定知识库成功（替换模式）")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"绑定知识库失败: {str(e)}")
        raise ValueError(f"绑定知识库失败: {str(e)}")

def create_robot_filter(db: Session, robot_uid: str, filter_type: int,
                       is_filter_groups: Optional[bool] = None,
                       is_filter_private: Optional[bool] = None,
                       is_filter_members: Optional[bool] = None,
                       whitelist_content: Optional[List[str]] = None,
                       blacklist_content: Optional[List[str]] = None,
                       whitelist_names: Optional[List[str]] = None,
                       blacklist_names: Optional[List[str]] = None) -> RobotFilters:
    """创建机器人过滤规则"""
    try:
        # 检查机器人是否存在
        robot = get_robot_by_uid(db, robot_uid)
        if not robot:
            raise ValueError("机器人不存在")
        
        # 检查是否已存在过滤规则
        existing_filter = db.query(RobotFilters).filter(
            and_(RobotFilters.robot_uid == robot_uid, RobotFilters.is_del == 0)
        ).first()
        
        if existing_filter:
            raise ValueError("机器人已存在过滤规则")
        
        # 转换列表为JSON字符串
        whitelist_content_json = json.dumps(whitelist_content) if whitelist_content else None
        blacklist_content_json = json.dumps(blacklist_content) if blacklist_content else None
        whitelist_names_json = json.dumps(whitelist_names) if whitelist_names else None
        blacklist_names_json = json.dumps(blacklist_names) if blacklist_names else None
        
        db_filter = RobotFilters(
            uid=str(uuid.uuid4()),
            filter_type=filter_type,
            is_filter_groups=1 if is_filter_groups else 0 if is_filter_groups is not None else None,
            is_filter_private=1 if is_filter_private else 0 if is_filter_private is not None else None,
            is_filter_members=1 if is_filter_members else 0 if is_filter_members is not None else None,
            whitelist_content=whitelist_content_json,
            blacklist_content=blacklist_content_json,
            whitelist_names=whitelist_names_json,
            blacklist_names=blacklist_names_json,
            robot_uid=robot_uid,
            is_del=0
        )
        
        db.add(db_filter)
        
        # 更新机器人的绑定过滤规则状态
        robot.is_bind_filter = 1
        
        db.commit()
        db.refresh(db_filter)
        logger.info(f"机器人过滤规则创建成功: {db_filter.uid}")
        return db_filter
    except Exception as e:
        db.rollback()
        logger.error(f"创建过滤规则失败: {str(e)}")
        raise ValueError(f"创建过滤规则失败: {str(e)}")

def get_robot_filter_by_robot_uid(db: Session, robot_uid: str) -> Optional[RobotFilters]:
    """根据机器人UID获取过滤规则"""
    return db.query(RobotFilters).filter(
        and_(RobotFilters.robot_uid == robot_uid, RobotFilters.is_del == 0)
    ).first()

def get_robot_knowledges(db: Session, robot_uid: str) -> List[str]:
    """获取机器人绑定的知识库UID列表"""
    relations = db.query(RobotsKnowledgesRelations).filter(
        and_(
            RobotsKnowledgesRelations.robot_uid == robot_uid,
            RobotsKnowledgesRelations.is_del == 0
        )
    ).all()
    
    return [relation.knowledge_uid for relation in relations]