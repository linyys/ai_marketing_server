from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

from db.point_record import PointRecord


def create_point_record(
    db: Session,
    from_user_uid: str,
    point: Decimal,
    record_type: int,
    record_desc: Optional[str] = None,
    function_name: Optional[str] = None,
    from_uid: Optional[str] = None,
) -> PointRecord:
    """创建积分变动记录"""
    pr = PointRecord(
        from_user_uid=from_user_uid,
        point=Decimal(point or 0).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP),
        record_type=record_type,
        record_desc=record_desc,
        function_name=function_name,
        from_uid=from_uid,
    )
    db.add(pr)
    db.commit()
    db.refresh(pr)
    return pr


def get_point_records_by_user(
    db: Session,
    from_user_uid: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    record_type: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[PointRecord], int]:
    """按用户查询积分记录，支持时间范围与类型过滤，返回列表与总数"""
    query = db.query(PointRecord).filter(PointRecord.from_user_uid == from_user_uid)

    if record_type is not None:
        query = query.filter(PointRecord.record_type == record_type)
    if start_time is not None:
        query = query.filter(PointRecord.created_time >= start_time)
    if end_time is not None:
        query = query.filter(PointRecord.created_time <= end_time)

    total = query.count()
    items = (
        query.order_by(PointRecord.created_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items, total


def list_point_records(
    db: Session,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    record_type: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[PointRecord], int]:
    """查询积分记录（不限定用户），用于审计统计"""
    query = db.query(PointRecord)

    if record_type is not None:
        query = query.filter(PointRecord.record_type == record_type)
    if start_time is not None:
        query = query.filter(PointRecord.created_time >= start_time)
    if end_time is not None:
        query = query.filter(PointRecord.created_time <= end_time)

    total = query.count()
    items = (
        query.order_by(PointRecord.created_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items, total