from sqlalchemy import Column, Integer, String, func, TIMESTAMP, Boolean, Index, CheckConstraint, ForeignKey, Text
from sqlalchemy.dialects.mysql import TINYINT
import uuid
from db.database import Base

class RobotFilters(Base):
    __tablename__ = "robot_filters"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), comment='过滤规则唯一标识')
    created_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), comment='创建时间')
    updated_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    is_del = Column(TINYINT(1), nullable=False, default=False, comment='是否删除：0-未删除，1-已删除')
    filter_type = Column(TINYINT(1), nullable=False, comment='过滤类型：0-黑名单 1-白名单 2-先通过白名单再过滤黑名单')
    is_filter_groups = Column(TINYINT(1), comment='是否过滤群聊：0-不过滤 1-过滤（仅微信和企业微信有效）')
    is_filter_private = Column(TINYINT(1), comment='是否过滤私聊：0-不过滤 1-过滤（仅微信和企业微信有效）')
    is_filter_members = Column(TINYINT(1), comment='是否过滤群成员：0-不过滤 1-过滤（仅微信和企业微信有效）')
    whitelist_content = Column(Text, comment='白名单内容（JSON格式存储多个值）')
    blacklist_content = Column(Text, comment='黑名单内容（JSON格式存储多个值）')
    whitelist_names = Column(Text, comment='白名单名称（JSON格式存储多个值，仅微信和企业微信有效）')
    blacklist_names = Column(Text, comment='黑名单名称（JSON格式存储多个值，仅微信和企业微信有效）')
    robot_uid = Column(String(36), ForeignKey('robots.uid', ondelete='CASCADE', onupdate='CASCADE'), unique=True, nullable=False, comment='机器人ID')
    
    __table_args__ = (
        Index('idx_robot_uid', 'robot_uid'),
        Index('idx_filter_type', 'filter_type'),
        Index('idx_is_del', 'is_del'),
        Index('idx_created_time', 'created_time'),
        CheckConstraint('filter_type IN (0, 1, 2)', name='chk_filter_type'),
        CheckConstraint('is_del IN (0, 1)', name='chk_is_del'),
        CheckConstraint('is_filter_groups IS NULL OR is_filter_groups IN (0, 1)', name='chk_is_filter_groups'),
        CheckConstraint('is_filter_private IS NULL OR is_filter_private IN (0, 1)', name='chk_is_filter_private'),
        CheckConstraint('is_filter_members IS NULL OR is_filter_members IN (0, 1)', name='chk_is_filter_members'),
        CheckConstraint(
            '((filter_type = 0 AND blacklist_content IS NOT NULL) OR '
            '(filter_type = 1 AND whitelist_content IS NOT NULL) OR '
            '(filter_type = 2 AND whitelist_content IS NOT NULL AND blacklist_content IS NOT NULL))',
            name='chk_filter_content'
        ),
    )
