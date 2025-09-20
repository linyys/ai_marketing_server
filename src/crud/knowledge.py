from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from db.knowledges import Knowledges
from db.robots_knowledges_relations import RobotsKnowledgesRelations
from typing import List, Optional
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

def create_knowledge(db: Session, name: str, content: str, description: str, from_user: Optional[str] = None) -> Knowledges:
    """创建知识库"""
    # 检查名称是否已存在
    existing_knowledge = get_knowledge_by_name(db, name)
    if existing_knowledge:
        raise ValueError("知识库名称已存在")
    
    try:
        db_knowledge = Knowledges(
            uid=str(uuid.uuid4()),
            name=name,
            content=content,
            description=description,
            from_user=from_user,
            is_del=0
        )
        db.add(db_knowledge)
        db.commit()
        db.refresh(db_knowledge)
        logger.info(f"知识库创建成功: {db_knowledge.uid}")
        return db_knowledge
    except Exception as e:
        db.rollback()
        logger.error(f"创建知识库失败: {str(e)}")
        raise ValueError(f"创建知识库失败: {str(e)}")

def get_knowledge_by_name(db: Session, name: str) -> Optional[Knowledges]:
    """根据名称获取知识库"""
    return db.query(Knowledges).filter(and_(Knowledges.name == name, Knowledges.is_del == 0)).first()

def get_knowledge_by_uid(db: Session, uid: str) -> Optional[Knowledges]:
    """根据UID获取知识库"""
    return db.query(Knowledges).filter(and_(Knowledges.uid == uid, Knowledges.is_del == 0)).first()

def get_knowledges(db: Session, skip: int = 0, limit: int = 20) -> List[Knowledges]:
    """获取知识库列表"""
    return db.query(Knowledges).filter(Knowledges.is_del == 0).offset(skip).limit(limit).all()

def get_knowledges_count(db: Session) -> int:
    """获取知识库总数"""
    return db.query(Knowledges).filter(Knowledges.is_del == 0).count()

def get_knowledges_by_user(db: Session, user_uid: str, skip: int = 0, limit: int = 20) -> List[Knowledges]:
    """获取指定用户的知识库列表"""
    return db.query(Knowledges).filter(
        and_(Knowledges.from_user == user_uid, Knowledges.is_del == 0)
    ).offset(skip).limit(limit).all()

def get_knowledges_by_user_count(db: Session, user_uid: str) -> int:
    """获取指定用户的知识库总数"""
    return db.query(Knowledges).filter(
        and_(Knowledges.from_user == user_uid, Knowledges.is_del == 0)
    ).count()

def get_public_knowledges(db: Session, skip: int = 0, limit: int = 20) -> List[Knowledges]:
    """获取公共知识库列表（from_user为空）"""
    return db.query(Knowledges).filter(
        and_(Knowledges.from_user.is_(None), Knowledges.is_del == 0)
    ).offset(skip).limit(limit).all()

def get_user_accessible_knowledges(db: Session, user_uid: str, skip: int = 0, limit: int = 20) -> List[Knowledges]:
    """获取用户可访问的知识库列表（自己的+公共的）"""
    return db.query(Knowledges).filter(
        and_(
            or_(Knowledges.from_user == user_uid, Knowledges.from_user.is_(None)),
            Knowledges.is_del == 0
        )
    ).offset(skip).limit(limit).all()

def get_user_accessible_knowledges_count(db: Session, user_uid: str) -> int:
    """获取用户可访问的知识库总数"""
    return db.query(Knowledges).filter(
        and_(
            or_(Knowledges.from_user == user_uid, Knowledges.from_user.is_(None)),
            Knowledges.is_del == 0
        )
    ).count()

def update_knowledge(db: Session, knowledge_uid: str, name: Optional[str] = None, 
                    content: Optional[str] = None, description: Optional[str] = None) -> Optional[Knowledges]:
    """更新知识库"""
    try:
        db_knowledge = get_knowledge_by_uid(db, knowledge_uid)
        if not db_knowledge:
            logger.warning(f"知识库不存在: {knowledge_uid}")
            return None
        
        # 检查名称是否已被其他知识库使用
        if name and name != db_knowledge.name:
            existing_knowledge = get_knowledge_by_name(db, name)
            if existing_knowledge and existing_knowledge.uid != knowledge_uid:
                raise ValueError("知识库名称已存在")
        
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if content is not None:
            update_data['content'] = content
        if description is not None:
            update_data['description'] = description
        
        if update_data:
            for key, value in update_data.items():
                setattr(db_knowledge, key, value)
            
            db.commit()
            db.refresh(db_knowledge)
            logger.info(f"知识库更新成功: {knowledge_uid}")
        
        return db_knowledge
    except Exception as e:
        db.rollback()
        logger.error(f"更新知识库失败: {str(e)}")
        raise ValueError(f"更新知识库失败: {str(e)}")

def delete_knowledge(db: Session, knowledge_uid: str) -> bool:
    """删除知识库（软删除）"""
    try:
        db_knowledge = get_knowledge_by_uid(db, knowledge_uid)
        if not db_knowledge:
            logger.warning(f"知识库不存在: {knowledge_uid}")
            return False
        
        db_knowledge.is_del = 1
        db.commit()
        logger.info(f"知识库删除成功: {knowledge_uid}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"删除知识库失败: {str(e)}")
        return False

def search_knowledges(db: Session, name: Optional[str] = None, content: Optional[str] = None, 
                     description: Optional[str] = None, from_user: Optional[str] = None,
                     start_time: Optional[datetime] = None, end_time: Optional[datetime] = None,
                     skip: int = 0, limit: int = 20) -> tuple[List[Knowledges], int]:
    """搜索知识库"""
    query = db.query(Knowledges).filter(Knowledges.is_del == 0)
    
    if name:
        query = query.filter(Knowledges.name.like(f"%{name}%"))
    if content:
        query = query.filter(Knowledges.content.like(f"%{content}%"))
    if description:
        query = query.filter(Knowledges.description.like(f"%{description}%"))
    if from_user:
        query = query.filter(Knowledges.from_user == from_user)
    if start_time:
        query = query.filter(Knowledges.created_time >= start_time)
    if end_time:
        query = query.filter(Knowledges.created_time <= end_time)
    
    total = query.count()
    knowledges = query.offset(skip).limit(limit).all()
    
    return knowledges, total

def search_user_accessible_knowledges(db: Session, user_uid: str, name: Optional[str] = None, 
                                     content: Optional[str] = None, description: Optional[str] = None,
                                     start_time: Optional[datetime] = None, end_time: Optional[datetime] = None,
                                     skip: int = 0, limit: int = 20) -> tuple[List[Knowledges], int]:
    """搜索用户可访问的知识库"""
    query = db.query(Knowledges).filter(
        and_(
            or_(Knowledges.from_user == user_uid, Knowledges.from_user.is_(None)),
            Knowledges.is_del == 0
        )
    )
    
    if name:
        query = query.filter(Knowledges.name.like(f"%{name}%"))
    if content:
        query = query.filter(Knowledges.content.like(f"%{content}%"))
    if description:
        query = query.filter(Knowledges.description.like(f"%{description}%"))
    if start_time:
        query = query.filter(Knowledges.created_time >= start_time)
    if end_time:
        query = query.filter(Knowledges.created_time <= end_time)
    
    total = query.count()
    knowledges = query.offset(skip).limit(limit).all()
    
    return knowledges, total

def check_knowledge_permission(db: Session, knowledge_uid: str, user_uid: str) -> tuple[bool, Optional[Knowledges]]:
    """检查用户对知识库的权限"""
    knowledge = get_knowledge_by_uid(db, knowledge_uid)
    if not knowledge:
        return False, None
    
    # 如果是公共知识库（from_user为空），用户可以查看但不能编辑
    if knowledge.from_user is None:
        return True, knowledge
    
    # 如果是用户自己的知识库，有完全权限
    if knowledge.from_user == user_uid:
        return True, knowledge
    
    # 其他情况无权限
    return False, knowledge

def get_knowledge_uids_by_robot_uid(db: Session, robot_uid: str) -> List[str]:
    """根据机器人UID获取关联的知识库ID列表"""
    try:
        relations = db.query(RobotsKnowledgesRelations).filter(
            and_(
                RobotsKnowledgesRelations.robot_uid == robot_uid,
                RobotsKnowledgesRelations.is_del == 0
            )
        ).all()
        
        knowledge_ids = [relation.knowledge_uid for relation in relations]
        logger.info(f"机器人 {robot_uid} 关联的知识库数量: {len(knowledge_ids)}")
        return knowledge_ids
    except Exception as e:
        logger.error(f"获取机器人 {robot_uid} 的知识库ID列表失败: {str(e)}")
        return []