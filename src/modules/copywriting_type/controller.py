from sqlalchemy.orm import Session
from fastapi import HTTPException
from crud import copywriting_type as crud_copywriting_type
from schemas.copywriting_type import CopywritingTypeCreate, CopywritingTypeUpdate, CopywritingTypeSearchParams


def create_copywriting_type(db: Session, copywriting_type: CopywritingTypeCreate, user_id: str):
    return crud_copywriting_type.create_copywriting_type(db, copywriting_type, user_id)


def get_copywriting_type(db: Session, copywriting_type_id: int):
    copywriting_type = crud_copywriting_type.get_copywriting_type(db, copywriting_type_id)
    if not copywriting_type:
        raise HTTPException(status_code=404, detail="文案类型不存在")
    return copywriting_type


def get_copywriting_type_by_uid(db: Session, copywriting_type_uid: str):
    copywriting_type = crud_copywriting_type.get_copywriting_type_by_uid(db, copywriting_type_uid)
    if not copywriting_type:
        raise HTTPException(status_code=404, detail="文案类型不存在")
    return copywriting_type


def search_copywriting_types(db: Session, params: CopywritingTypeSearchParams):
    return crud_copywriting_type.search_copywriting_types(db, params)


def update_copywriting_type(db: Session, copywriting_type_id: int, copywriting_type: CopywritingTypeUpdate, user_id: str):
    db_copywriting_type = crud_copywriting_type.update_copywriting_type(db, copywriting_type_id, copywriting_type, user_id)
    if not db_copywriting_type:
        raise HTTPException(status_code=404, detail="文案类型不存在")
    return db_copywriting_type


def delete_copywriting_type(db: Session, copywriting_type_id: int):
    db_copywriting_type = crud_copywriting_type.delete_copywriting_type(db, copywriting_type_id)
    if not db_copywriting_type:
        raise HTTPException(status_code=404, detail="文案类型不存在")
    return {"message": "删除成功"}