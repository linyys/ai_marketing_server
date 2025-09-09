from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from utils.auth import get_current_user
from schemas.copywriting_type import CopywritingTypeCreate, CopywritingTypeUpdate, CopywritingTypeOut, CopywritingTypeSearchParams
from modules.copywriting_type import controller

router = APIRouter(prefix="/copywriting-types", tags=["文案类型"])


@router.post("/", response_model=CopywritingTypeOut, summary="创建文案类型")
def create_copywriting_type(
    copywriting_type: CopywritingTypeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return controller.create_copywriting_type(db, copywriting_type, current_user.uid)


@router.get("/{copywriting_type_id}", response_model=CopywritingTypeOut, summary="根据ID获取文案类型")
def get_copywriting_type(
    copywriting_type_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return controller.get_copywriting_type(db, copywriting_type_id)


@router.get("/uid/{copywriting_type_uid}", response_model=CopywritingTypeOut, summary="根据UID获取文案类型")
def get_copywriting_type_by_uid(
    copywriting_type_uid: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return controller.get_copywriting_type_by_uid(db, copywriting_type_uid)


@router.get("/", summary="搜索文案类型")
def search_copywriting_types(
    name: str = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    params = CopywritingTypeSearchParams(name=name, page=page, page_size=page_size)
    return controller.search_copywriting_types(db, params)


@router.put("/{copywriting_type_id}", response_model=CopywritingTypeOut, summary="更新文案类型")
def update_copywriting_type(
    copywriting_type_id: int,
    copywriting_type: CopywritingTypeUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return controller.update_copywriting_type(db, copywriting_type_id, copywriting_type, current_user.uid)


@router.delete("/{copywriting_type_id}", summary="删除文案类型")
def delete_copywriting_type(
    copywriting_type_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return controller.delete_copywriting_type(db, copywriting_type_id)