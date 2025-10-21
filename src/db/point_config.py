from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Index
from sqlalchemy.dialects.mysql import TINYINT
from db.database import Base

class PointConfig(Base):
    __tablename__ = "point_configs"

    id = Column(Integer, primary_key=True, index=True)
    function_id = Column(String(64), unique=True, index=True, nullable=False, comment='功能唯一ID')
    function_name = Column(String(100), nullable=False, comment='功能显示名称')
    workflow_id = Column(String(64), index=True, nullable=False, comment='计费所绑定的工作流ID')
    consume = Column(Integer, nullable=False, default=0, comment='每单位消耗的积分数')
    measure_unit = Column(TINYINT(1), nullable=False, default=1, comment='计量单位：0-每字符、1-每次调用、2-每分钟')
    is_enable = Column(TINYINT(1), nullable=False, default=1, comment='是否启用：1启用，0禁用')

    created_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_workflow_id', 'workflow_id'),
    )