from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Index, Text
from sqlalchemy.dialects.mysql import TINYINT
from db.database import Base
import uuid

class PointRecord(Base):
    __tablename__ = "point_records"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    from_user_uid = Column(String(36), index=True, nullable=False, comment='对应用户UID')
    point = Column(Integer, nullable=False, comment='本次变动积分数（记录为正数）')
    record_type = Column(TINYINT(1), nullable=False, comment='记录类型：1-积分卡充值、2-消费')
    record_desc = Column(Text, nullable=True, comment='记录描述')

    created_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_from_user_uid', 'from_user_uid'),
        Index('idx_record_type', 'record_type'),
        Index('idx_created_time', 'created_time'),
    )