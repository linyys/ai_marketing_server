from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from db.point_config import PointConfig


def create_point_config(
    db: Session,
    function_id: str,
    function_name: str,
    workflow_id: str,
    consume: int,
    measure_unit: int,
    is_enable: int = 1,
) -> PointConfig:
    """创建积分配置"""
    exists = (
        db.query(PointConfig)
        .filter(PointConfig.function_id == function_id)
        .first()
    )
    if exists:
        raise ValueError("function_id已存在")
    pc = PointConfig(
        function_id=function_id,
        function_name=function_name,
        workflow_id=workflow_id,
        consume=consume,
        measure_unit=measure_unit,
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


def get_point_config_by_function_id(db: Session, function_id: str) -> Optional[PointConfig]:
    """根据function_id获取积分配置"""
    return (
        db.query(PointConfig)
        .filter(PointConfig.function_id == function_id)
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
    function_id: str,
    function_name: Optional[str] = None,
    workflow_id: Optional[str] = None,
    consume: Optional[int] = None,
    measure_unit: Optional[int] = None,
    is_enable: Optional[int] = None,
) -> Optional[PointConfig]:
    """更新积分配置"""
    pc = get_point_config_by_function_id(db, function_id)
    if not pc:
        return None

    if function_name is not None:
        pc.function_name = function_name
    if workflow_id is not None:
        pc.workflow_id = workflow_id
    if consume is not None:
        pc.consume = consume
    if measure_unit is not None:
        pc.measure_unit = measure_unit
    if is_enable is not None:
        pc.is_enable = is_enable

    pc.updated_time = datetime.now()
    db.commit()
    db.refresh(pc)
    return pc


def delete_point_config(db: Session, function_id: str) -> bool:
    """删除积分配置（硬删除）"""
    pc = get_point_config_by_function_id(db, function_id)
    if not pc:
        return False
    db.delete(pc)
    db.commit()
    return True