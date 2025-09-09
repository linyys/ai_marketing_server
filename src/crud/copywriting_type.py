from sqlalchemy.orm import Session
from sqlalchemy import func
from db.copywriting_types import CopywritingType
from schemas.copywriting_type import CopywritingTypeCreate, CopywritingTypeUpdate, CopywritingTypeSearchParams


def create_copywriting_type(db: Session, copywriting_type: CopywritingTypeCreate, user_id: str):
    db_copywriting_type = CopywritingType(**copywriting_type.dict(), updated_user_id=user_id)
    db.add(db_copywriting_type)
    db.commit()
    db.refresh(db_copywriting_type)
    return db_copywriting_type


def get_copywriting_type(db: Session, copywriting_type_id: int):
    return db.query(CopywritingType).filter(CopywritingType.id == copywriting_type_id, CopywritingType.is_del == 0).first()


def get_copywriting_type_by_uid(db: Session, copywriting_type_uid: str):
    return db.query(CopywritingType).filter(CopywritingType.uid == copywriting_type_uid, CopywritingType.is_del == 0).first()


def search_copywriting_types(db: Session, params: CopywritingTypeSearchParams):
    query = db.query(CopywritingType).filter(CopywritingType.is_del == 0)

    if params.name:
        query = query.filter(CopywritingType.name.like(f"%{params.name}%"))

    total = query.count()

    items = query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()

    return {"total": total, "items": items}


def update_copywriting_type(db: Session, copywriting_type_id: int, copywriting_type: CopywritingTypeUpdate, user_id: str):
    db_copywriting_type = get_copywriting_type(db, copywriting_type_id)
    if db_copywriting_type:
        update_data = copywriting_type.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_copywriting_type, key, value)
        db_copywriting_type.updated_user_id = user_id
        db.commit()
        db.refresh(db_copywriting_type)
    return db_copywriting_type


def delete_copywriting_type(db: Session, copywriting_type_id: int):
    db_copywriting_type = get_copywriting_type(db, copywriting_type_id)
    if db_copywriting_type:
        db_copywriting_type.is_del = 1
        db.commit()
    return db_copywriting_type