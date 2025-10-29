from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Numeric, UniqueConstraint
from sqlalchemy.dialects.mysql import TINYINT
from db.database import Base
import uuid

class PointConfig(Base):
    __tablename__ = "point_configs"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    function_name = Column(String(100), nullable=False, comment='功能显示名称')
    workflow_id = Column(String(64), nullable=False, comment='计费所绑定的工作流ID')
    measure_unit = Column(TINYINT(1), nullable=False, default=1, comment='计量类型：1-每字符、2-每次调用、3-每分钟')
    token = Column(Numeric(18, 6), nullable=False, default=0, comment='消耗的积分（可为小数）')
    unit = Column(Integer, nullable=False, default=1, comment='计费数量（例如每100字符）')
    is_enable = Column(TINYINT(1), nullable=False, default=1, comment='是否启用：1启用，0禁用')

    created_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('workflow_id', name='uniq_workflow_id'),
    )