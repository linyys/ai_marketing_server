from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from decimal import Decimal, ROUND_HALF_UP
from crud.point_config import (
    create_point_config,
    update_point_config,
    list_point_configs,
    get_point_config_by_uid,
)
from crud.point_record import (
    get_point_records_by_user,
)


def _point_config_to_dict(pc) -> Dict:
    if pc is None:
        return None
    return {
        "id": pc.id,
        "uid": pc.uid,
        "function_name": pc.function_name,
        "workflow_id": pc.workflow_id,
        "token": str(pc.token),
        "measure_unit": pc.measure_unit,
        "unit": pc.unit,
        "is_enable": pc.is_enable,
        "created_time": pc.created_time,
        "updated_time": pc.updated_time,
    }


def _point_record_to_dict(pr) -> Dict:
    if pr is None:
        return None
    return {
        "id": pr.id,
        "uid": pr.uid,
        "from_user_uid": pr.from_user_uid,
        "function_name": pr.function_name,
        "from_uid": pr.from_uid,
        "point": str(Decimal(pr.point or 0).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP).normalize()),
        "record_type": pr.record_type,
        "record_desc": pr.record_desc,
        "created_time": pr.created_time,
        "updated_time": pr.updated_time,
    }


# 配置相关服务函数

def create_config_service(
    db: Session,
    function_name: str,
    workflow_id: str,
    token: "Decimal",
    measure_unit: int,
    unit: int,
    is_enable: int = 1,
):
    pc = create_point_config(
        db=db,
        function_name=function_name,
        workflow_id=workflow_id,
        token=token,
        measure_unit=measure_unit,
        unit=unit,
        is_enable=is_enable,
    )
    return _point_config_to_dict(pc)


def update_config_service(
    db: Session,
    uid: str,
    function_name: Optional[str] = None,
    workflow_id: Optional[str] = None,
    token: Optional["Decimal"] = None,
    measure_unit: Optional[int] = None,
    unit: Optional[int] = None,
    is_enable: Optional[int] = None,
):
    pc = update_point_config(
        db=db,
        uid=uid,
        function_name=function_name,
        workflow_id=workflow_id,
        token=token,
        measure_unit=measure_unit,
        unit=unit,
        is_enable=is_enable,
    )
    return _point_config_to_dict(pc)


def list_configs_service(db: Session) -> List[Dict]:
    items = list_point_configs(db)
    return [_point_config_to_dict(pc) for pc in items]


def get_config_service(db: Session, uid: str) -> Optional[Dict]:
    pc = get_point_config_by_uid(db, uid)
    return _point_config_to_dict(pc)


# 记录相关服务函数

def list_point_records_by_user_service(db: Session, uid: str) -> Dict:
    items, total = get_point_records_by_user(db, from_user_uid=uid)
    return {
        "total": total,
        "items": [_point_record_to_dict(pr) for pr in items],
    }