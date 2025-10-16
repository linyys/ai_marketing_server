from sqlalchemy import Column, Integer, String, func, TIMESTAMP, ForeignKey, Index, UniqueConstraint, Date
from sqlalchemy.dialects.mysql import TINYINT
import uuid
from db.database import Base


class PlatformData(Base):
    __tablename__ = "platform_data"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    is_del = Column(TINYINT(1), default=False, comment='是否删除：False-未删除，True-已删除')
    created_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    from_video = Column(String(36), ForeignKey('platform_video.uid', ondelete='CASCADE', onupdate='CASCADE'), nullable=True, comment='来自于对应platform_video的uid')
    stat_date = Column(Date, nullable=True, comment='统计日期（每日一条）')
    play = Column(Integer, nullable=False, default=0, comment='播放量')
    like_count = Column(Integer, nullable=False, default=0, comment='点赞数量')
    comment_count = Column(Integer, nullable=False, default=0, comment='评论数量')
    share = Column(Integer, nullable=False, default=0, comment='分享数量')

    __table_args__ = (
        Index('idx_from_video', 'from_video'),
        Index('idx_stat_date', 'stat_date'),
        UniqueConstraint('from_video', 'stat_date', name='uk_video_stat_date'),
    )