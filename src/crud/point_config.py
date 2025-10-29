from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from db.point_config import PointConfig


def create_point_config(
    db: Session,
    function_name: str,
    workflow_id: str,
    token: Decimal,
    measure_unit: int = 1,
    unit: int = 1,
    is_enable: int = 1,
) -> PointConfig:
    """创建积分配置（uid自动生成）"""
    pc = PointConfig(
        function_name=function_name,
        workflow_id=workflow_id,
        token=token,
        measure_unit=measure_unit,
        unit=unit,
        is_enable=is_enable,
    )
    db.add(pc)
    db.commit()
    db.refresh(pc)
    return pc


def get_point_config_by_workflow_id(db: Session, workflow_id: str) -> Optional[PointConfig]:
    """根据workflow_id获取启用的积分配置"""
    return (
        db.query(PointConfig)
        .filter(PointConfig.workflow_id == workflow_id, PointConfig.is_enable == 1)
        .first()
    )


def get_point_config_by_uid(db: Session, uid: str) -> Optional[PointConfig]:
    """根据uid获取积分配置"""
    return (
        db.query(PointConfig)
        .filter(PointConfig.uid == uid)
        .first()
    )


def list_point_configs(db: Session, skip: int = 0, limit: int = 20) -> List[PointConfig]:
    """分页获取积分配置列表"""
    return (
        db.query(PointConfig)
        .order_by(PointConfig.created_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_point_config(
    db: Session,
    uid: str,
    function_name: Optional[str] = None,
    workflow_id: Optional[str] = None,
    token: Optional[Decimal] = None,
    measure_unit: Optional[int] = None,
    unit: Optional[int] = None,
    is_enable: Optional[int] = None,
) -> Optional[PointConfig]:
    """更新积分配置（按uid）"""
    pc = get_point_config_by_uid(db, uid)
    if not pc:
        return None

    if function_name is not None:
        pc.function_name = function_name
    if workflow_id is not None:
        pc.workflow_id = workflow_id
    if token is not None:
        pc.token = token
    if measure_unit is not None:
        pc.measure_unit = measure_unit
    if unit is not None:
        pc.unit = unit
    if is_enable is not None:
        pc.is_enable = is_enable

    pc.updated_time = datetime.now()
    db.commit()
    db.refresh(pc)
    return pc


def delete_point_config(db: Session, uid: str) -> bool:
    """删除积分配置（硬删除，按uid）"""
    pc = get_point_config_by_uid(db, uid)
    if not pc:
        return False
    db.delete(pc)
    db.commit()
    return True