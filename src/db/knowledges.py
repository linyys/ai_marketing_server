from sqlalchemy import Column, Integer, String, func, TIMESTAMP, Boolean
from sqlalchemy.dialects.mysql import TINYINT, LONGTEXT
import uuid
from db.database import Base

class Knowledges(Base):
    __tablename__ = "knowledges"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    is_del = Column(TINYINT(1), default=False, comment='是否删除：False-未删除，True-已删除')
    created_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    from_user = Column(String(36), nullable=True, comment='创建用户ID')
    name = Column(String(50), nullable=False, comment='名称')
    content = Column(LONGTEXT, nullable=False, comment='内容')
    description = Column(String(255), nullable=False, comment='描述')