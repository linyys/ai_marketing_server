from sqlalchemy import Column, Integer, String, func, TIMESTAMP, Boolean
from sqlalchemy.dialects.mysql import TINYINT, LONGTEXT
import uuid
from db.database import Base

class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    is_del = Column(TINYINT(1), default=0, comment='是否删除：0-未删除，1-已删除')
    created_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    from_user = Column(String(36), nullable=True, comment='创建用户ID')
    name = Column(String(50), nullable=False, comment='名称')
    content = Column(LONGTEXT, nullable=False, comment='内容')
    description = Column(String(255), nullable=False, comment='描述')
    platform = Column(TINYINT(1), nullable=False, comment='平台：0-抖音，1-微信视频号，2-小红书')
    time_cron = Column(String(255), nullable=False, comment='定时任务表达式')
    is_system = Column(TINYINT(1), default=0, comment='是否系统级提醒：0-否，1-是')
    one_time = Column(TINYINT(1), default=0, comment='是否一次性任务：0-否，1-是')
