from sqlalchemy import Column, Integer, String, func, TIMESTAMP, Boolean
import uuid
from db.database import Base

class CopywritingTypes(Base):
    __tablename__ = "copywriting_types"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    is_del = Column(Boolean, default=False, comment='是否删除：False-未删除，True-已删除')
    created_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    updated_admin_uid = Column(String(36), nullable=False, comment='更新管理员ID')
    name = Column(String(50), nullable=False, comment='名称')
    prompt = Column(String(255), nullable=False, comment='提示词')
    template = Column(String(255), nullable=False, comment='模板')
    description = Column(String(255), nullable=False, comment='描述')
    icon = Column(String(15), nullable=False, comment='图标')