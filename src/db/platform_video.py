from sqlalchemy import Column, Integer, String, func, TIMESTAMP, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.mysql import TINYINT, LONGTEXT
import uuid
from db.database import Base


class PlatformVideo(Base):
    __tablename__ = "platform_video"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    is_del = Column(TINYINT(1), default=False, comment='是否删除：False-未删除，True-已删除')
    created_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    from_bind = Column(String(36), ForeignKey('platform_bind.uid', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, comment='对应平台绑定的UID')
    platform_video_id = Column(String(255), nullable=False, comment='平台侧视频ID（如抖音视频ID）')
    title = Column(String(255), nullable=True, comment='视频标题')
    url = Column(LONGTEXT, nullable=True, comment='视频URL')
    publish_time = Column(Integer, nullable=True, comment='视频发布时间')
    cover = Column(LONGTEXT, nullable=True, comment='封面URL')

    __table_args__ = (
        UniqueConstraint('from_bind', 'platform_video_id', name='uk_bind_platform_video_id'),
        Index('idx_video_from_bind', 'from_bind'),
    )