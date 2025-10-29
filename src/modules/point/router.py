from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from utils.auth import get_current_admin, get_current_admin_or_user
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

from modules.point.controller import (
    create_config_service,
    update_config_service,
    list_configs_service,
    get_config_service,
    list_point_records_by_user_service,
)

router = APIRouter(tags=["积分"], prefix="/point")


class PointConfigCreate(BaseModel):
    function_name: str
    workflow_id: str
    token: Decimal
    measure_unit: int
    unit: int
    is_enable: int = 1


class PointConfigUpdate(BaseModel):
    uid: str
    function_name: Optional[str] = None
    workflow_id: Optional[str] = None
    token: Optional[Decimal] = None
    measure_unit: Optional[int] = None
    unit: Optional[int] = None
    is_enable: Optional[int] = None


@router.post("/create/config")
def create_config(
    data: PointConfigCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
):
    return create_config_service(
        db=db,
        function_name=data.function_name,
        workflow_id=data.workflow_id,
        token=data.token,
        measure_unit=data.measure_unit,
        unit=data.unit,
        is_enable=data.is_enable,
    )


@router.post("/update/config")
def update_config(
    data: PointConfigUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
):
    return update_config_service(
        db=db,
        uid=data.uid,
        function_name=data.function_name,
        workflow_id=data.workflow_id,
        token=data.token,
        measure_unit=data.measure_unit,
        unit=data.unit,
        is_enable=data.is_enable,
    )


@router.get("/config/all")
def get_all_configs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user),
):
    return list_configs_service(db)


@router.get("/config/{uid}")
def get_config(
    uid: str,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
):
    return get_config_service(db, uid)


@router.get("/record/all/{uid}")
def get_records_by_user(
    uid: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user),
):
    return list_point_records_by_user_service(db, uid)