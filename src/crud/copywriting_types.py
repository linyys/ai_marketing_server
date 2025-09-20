from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from db.copywriting_types import CopywritingTypes
from typing import List, Optional, Tuple
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

def create_copywriting_type(
    db: Session,
    name: str,
    prompt: str,
    template: str,
    description: str,
    template_type: int,
    icon: str,
    updated_admin_uid: str
) -> CopywritingTypes:
    """创建文案类型"""
    # 检查名称是否已存在
    existing_type = get_copywriting_type_by_name(db, name)
    if existing_type:
        raise ValueError("文案类型名称已存在")
    
    type_uid = str(uuid.uuid4())
    
    db_copywriting_type = CopywritingTypes(
        uid=type_uid,
        name=name,
        prompt=prompt,
        template=template,
        description=description,
        template_type=template_type,
        icon=icon,
        updated_admin_uid=updated_admin_uid
    )
    
    db.add(db_copywriting_type)
    db.commit()
    db.refresh(db_copywriting_type)
    
    logger.info(f"CopywritingType created: {db_copywriting_type.name} ({db_copywriting_type.uid})")
    return db_copywriting_type

def get_copywriting_type_by_id(db: Session, type_id: int) -> Optional[CopywritingTypes]:
    """根据ID获取文案类型"""
    return db.query(CopywritingTypes).filter(
        and_(CopywritingTypes.id == type_id, CopywritingTypes.is_del == 0)
    ).first()

def get_copywriting_type_by_uid(db: Session, uid: str) -> Optional[CopywritingTypes]:
    """根据UID获取文案类型"""
    return db.query(CopywritingTypes).filter(
        and_(CopywritingTypes.uid == uid, CopywritingTypes.is_del == 0)
    ).first()

def get_copywriting_type_by_name(db: Session, name: str) -> Optional[CopywritingTypes]:
    """根据名称获取文案类型"""
    return db.query(CopywritingTypes).filter(
        and_(CopywritingTypes.name == name, CopywritingTypes.is_del == 0)
    ).first()

def get_copywriting_types(db: Session, skip: int = 0, limit: int = 20) -> List[CopywritingTypes]:
    """获取文案类型列表（未删除）"""
    return db.query(CopywritingTypes).filter(
        CopywritingTypes.is_del == 0
    ).offset(skip).limit(limit).all()

def get_copywriting_types_count(db: Session) -> int:
    """获取文案类型总数（未删除）"""
    return db.query(CopywritingTypes).filter(
        CopywritingTypes.is_del == 0
    ).count()

def update_copywriting_type(
    db: Session,
    uid: str,
    updated_admin_uid: str,
    name: Optional[str] = None,
    prompt: Optional[str] = None,
    template: Optional[str] = None,
    description: Optional[str] = None,
    template_type: Optional[int] = None,
    icon: Optional[str] = None
) -> Optional[CopywritingTypes]:
    """更新文案类型"""
    copywriting_type = get_copywriting_type_by_uid(db, uid)
    if not copywriting_type:
        return None
    
    # 如果要更新名称，检查新名称是否已存在
    if name and name != copywriting_type.name:
        existing_type = get_copywriting_type_by_name(db, name)
        if existing_type:
            raise ValueError("文案类型名称已存在")
        copywriting_type.name = name
    
    if prompt is not None:
        copywriting_type.prompt = prompt
    if template is not None:
        copywriting_type.template = template
    if description is not None:
        copywriting_type.description = description
    if template_type is not None:
        copywriting_type.template_type = template_type
    if icon is not None:
        copywriting_type.icon = icon
    
    copywriting_type.updated_admin_uid = updated_admin_uid
    copywriting_type.updated_time = datetime.now()
    
    db.commit()
    db.refresh(copywriting_type)
    
    logger.info(f"CopywritingType updated: {copywriting_type.name} ({copywriting_type.uid})")
    return copywriting_type

def soft_delete_copywriting_type(db: Session, uid: str, updated_admin_uid: str) -> bool:
    """软删除文案类型"""
    copywriting_type = get_copywriting_type_by_uid(db, uid)
    if not copywriting_type:
        return False
    
    copywriting_type.is_del = 1
    copywriting_type.updated_admin_uid = updated_admin_uid
    copywriting_type.updated_time = datetime.now()
    
    db.commit()
    
    logger.info(f"CopywritingType soft deleted: {copywriting_type.name} ({copywriting_type.uid})")
    return True

def search_copywriting_types(
    db: Session,
    name: Optional[str] = None,
    template_type: Optional[int] = None,
    is_del: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[CopywritingTypes], int]:
    """根据多个条件搜索文案类型"""
    query = db.query(CopywritingTypes)
    
    # 默认只查询未删除的记录
    if is_del is None:
        query = query.filter(CopywritingTypes.is_del == 0)
    else:
        query = query.filter(CopywritingTypes.is_del == is_del)
    
    if name:
        query = query.filter(CopywritingTypes.name.like(f"%{name}%"))
    
    if template_type is not None:
        query = query.filter(CopywritingTypes.template_type == template_type)
    
    if start_time:
        query = query.filter(CopywritingTypes.created_time >= start_time)
    
    if end_time:
        query = query.filter(CopywritingTypes.created_time <= end_time)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    copywriting_types = query.offset(skip).limit(limit).all()
    
    return copywriting_types, total