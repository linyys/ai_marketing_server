from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from db.knowledges import Knowledge
from schemas.knowledge import KnowledgeCreate, KnowledgeUpdate, KnowledgeSearchParams
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_knowledge_by_id(db: Session, knowledge_id: int) -> Optional[Knowledge]:
    """根据ID获取知识库"""
    return db.query(Knowledge).filter(
        and_(Knowledge.id == knowledge_id, Knowledge.is_del == 0)
    ).first()

def get_knowledge_by_uid(db: Session, uid: str) -> Optional[Knowledge]:
    """根据UID获取知识库"""
    return db.query(Knowledge).filter(
        and_(Knowledge.uid == uid, Knowledge.is_del == 0)
    ).first()

def get_knowledges(db: Session, skip: int = 0, limit: int = 20) -> List[Knowledge]:
    """获取知识库列表"""
    return db.query(Knowledge).filter(
        Knowledge.is_del == 0
    ).offset(skip).limit(limit).all()

def get_knowledges_count(db: Session) -> int:
    """获取知识库总数"""
    return db.query(Knowledge).filter(Knowledge.is_del == 0).count()

def create_knowledge(db: Session, knowledge: KnowledgeCreate) -> Knowledge:
    """创建知识库"""
    try:
        db_knowledge = Knowledge(
            name=knowledge.name,
            content=knowledge.content,
            description=knowledge.description,
            updated_admin_uid=knowledge.updated_admin_uid
        )
        db.add(db_knowledge)
        db.commit()
        db.refresh(db_knowledge)
        logger.info(f"Knowledge created successfully: {db_knowledge.uid}")
        return db_knowledge
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating knowledge: {e}")
        raise e

def update_knowledge(db: Session, knowledge_id: int, update_data: KnowledgeUpdate) -> Optional[Knowledge]:
    """更新知识库"""
    try:
        db_knowledge = get_knowledge_by_id(db, knowledge_id)
        if not db_knowledge:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return db_knowledge
        
        for field, value in update_dict.items():
            if hasattr(db_knowledge, field):
                setattr(db_knowledge, field, value)
        
        db_knowledge.updated_time = datetime.now()
        db.commit()
        db.refresh(db_knowledge)
        logger.info(f"Knowledge updated successfully: {db_knowledge.uid}")
        return db_knowledge
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating knowledge {knowledge_id}: {e}")
        raise e

def soft_delete_knowledge(db: Session, knowledge_id: int) -> bool:
    """软删除知识库"""
    try:
        db_knowledge = get_knowledge_by_id(db, knowledge_id)
        if not db_knowledge:
            return False
        
        db_knowledge.is_del = 1
        db_knowledge.updated_time = datetime.now()
        db.commit()
        logger.info(f"Knowledge soft deleted successfully: {db_knowledge.uid}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error soft deleting knowledge {knowledge_id}: {e}")
        raise e

def search_knowledges(db: Session, search_params: KnowledgeSearchParams, skip: int = 0, limit: int = 20) -> tuple[List[Knowledge], int]:
    """搜索知识库"""
    try:
        query = db.query(Knowledge).filter(Knowledge.is_del == 0)
        
        if search_params.name:
            query = query.filter(Knowledge.name.like(f"%{search_params.name}%"))
        
        if search_params.content:
            query = query.filter(Knowledge.content.like(f"%{search_params.content}%"))
        
        if search_params.description:
            query = query.filter(Knowledge.description.like(f"%{search_params.description}%"))
        
        if search_params.updated_admin_uid:
            query = query.filter(Knowledge.updated_admin_uid == search_params.updated_admin_uid)
        
        if search_params.start_time:
            query = query.filter(Knowledge.created_time >= search_params.start_time)
        
        if search_params.end_time:
            query = query.filter(Knowledge.created_time <= search_params.end_time)
        
        total = query.count()
        knowledges = query.offset(skip).limit(limit).all()
        
        return knowledges, total
    except Exception as e:
        logger.error(f"Error searching knowledges: {e}")
        raise e

def batch_delete_knowledges(db: Session, knowledge_ids: List[int]) -> bool:
    """批量删除知识库"""
    try:
        db.query(Knowledge).filter(
            and_(Knowledge.id.in_(knowledge_ids), Knowledge.is_del == 0)
        ).update(
            {Knowledge.is_del: 1, Knowledge.updated_time: datetime.now()},
            synchronize_session=False
        )
        db.commit()
        logger.info(f"Batch deleted knowledges: {knowledge_ids}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch deleting knowledges {knowledge_ids}: {e}")
        raise e

def get_knowledge_stats(db: Session) -> dict:
    """获取知识库统计信息"""
    try:
        total_count = db.query(Knowledge).filter(Knowledge.is_del == 0).count()
        today = datetime.now().date()
        today_count = db.query(Knowledge).filter(
            and_(
                Knowledge.is_del == 0,
                Knowledge.created_time >= today
            )
        ).count()
        
        return {
            "total_count": total_count,
            "today_count": today_count
        }
    except Exception as e:
        logger.error(f"Error getting knowledge stats: {e}")
        raise e