from sqlalchemy import Column, Integer, String, func, TIMESTAMP, Index, CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.mysql import TINYINT
import uuid
from db.database import Base

class RobotsKnowledgesRelations(Base):
    __tablename__ = "robots_knowledges_relations"
    id = Column(Integer, primary_key=True, index=True)
    created_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), comment='创建时间')
    updated_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    robot_uid = Column(String(36), ForeignKey('robots.uid', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, comment='机器人ID')
    knowledge_uid = Column(String(36), nullable=False, comment='知识库ID')
    is_del = Column(TINYINT(1), nullable=False, default=False, comment='是否删除：0-未删除，1-已删除')
    
    __table_args__ = (
        UniqueConstraint('robot_uid', 'knowledge_uid', name='uk_robot_knowledge'),
        Index('idx_robot_uid', 'robot_uid'),
        Index('idx_knowledge_uid', 'knowledge_uid'),
        Index('idx_is_del', 'is_del'),
        Index('idx_created_time', 'created_time'),
        CheckConstraint('is_del IN (0, 1)', name='chk_is_del'),
    )
