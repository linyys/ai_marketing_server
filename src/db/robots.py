from sqlalchemy import Column, Integer, String, func, TIMESTAMP, Boolean, Index, CheckConstraint, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT
import uuid
from db.database import Base

class Robots(Base):
    __tablename__ = "robots"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()), comment='机器人唯一标识')
    is_del = Column(TINYINT(1), nullable=False, default=False, comment='是否删除：0-未删除，1-已删除')
    is_enable = Column(TINYINT(1), nullable=False, default=False, comment='是否启用：0-未启用，1-已启用')
    created_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), comment='创建时间')
    updated_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    name = Column(String(50), nullable=False, comment='机器人名称')
    reply_type = Column(TINYINT(1), nullable=False, comment='回复类型：0-评论 1-私信 2-群聊 3-私聊')
    account = Column(String(255), comment='账号')
    password = Column(String(255), comment='密码')
    platform = Column(TINYINT(1), nullable=False, comment='平台：0-微信 1-企业微信 3-抖音 4-小红书')
    login_type = Column(TINYINT(1), nullable=False, comment='登录类型：0-账号密码登录 1-扫码登录')
    description = Column(String(255), nullable=False, comment='描述')
    from_user_uid = Column(String(36), ForeignKey('users.uid', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, comment='来源用户ID')
    is_bind_knowledges = Column(TINYINT(1), nullable=False, default=False, comment='是否绑定知识库：0-未绑定，1-已绑定')
    is_bind_filter = Column(TINYINT(1), nullable=False, default=False, comment='是否绑定过滤：0-未绑定，1-已绑定')
    __table_args__ = (
        Index('idx_platform', 'platform'),
        Index('idx_is_del_is_enable', 'is_del', 'is_enable'),
        Index('idx_created_time', 'created_time'),
        Index('idx_from_user_uid', 'from_user_uid'),
        CheckConstraint('platform IN (0, 1, 3, 4)', name='chk_platform'),
        CheckConstraint('login_type IN (0, 1)', name='chk_login_type'),
        CheckConstraint('reply_type IN (0, 1, 2, 3)', name='chk_reply_type'),
        CheckConstraint('is_del IN (0, 1)', name='chk_is_del'),
        CheckConstraint('is_enable IN (0, 1)', name='chk_is_enable'),
        CheckConstraint(
            '((platform IN (0, 1) AND login_type = 1) OR (platform IN (3, 4) AND login_type = 0))',
            name='chk_platform_login_type'
        ),
        CheckConstraint(
            '((platform IN (0, 1) AND reply_type IN (2, 3)) OR (platform IN (3, 4) AND reply_type IN (0, 1)))',
            name='chk_platform_reply_type'
        ),
    )