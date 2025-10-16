from sqlalchemy import Column, Integer, String, func, TIMESTAMP, Boolean
from sqlalchemy.dialects.mysql import TINYINT, LONGTEXT
import uuid
from db.database import Base

class PlatformBind(Base):
    __tablename__ = "platform_bind"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    is_del = Column(TINYINT(1), default=False, comment='是否删除：False-未删除，True-已删除')
    created_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    from_user = Column(String(36), nullable=False, comment='创建用户ID')
    type = Column(TINYINT(1), nullable=False, comment='类型：0-小红书，1-抖音')
    url = Column(String(255), nullable=False, comment='绑定的URL')
    user_name = Column(String(255), nullable=False, comment='绑定平台的用户名')
    user_desc = Column(String(255), nullable=False, comment='绑定平台的用户简介')
    avatar = Column(String(255), nullable=False, comment='绑定平台的用户头像')
