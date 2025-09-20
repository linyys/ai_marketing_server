from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.copywriting_types import (
    CopywritingTypeCreate, CopywritingTypeUpdate, CopywritingTypeOut,
    CopywritingTypeSearchParams, CopywritingTypeListResponse, CopywritingTypeDelete
)
from modules.copywriting_types.controller import (
    create_copywriting_type_service, get_copywriting_type_service,
    get_copywriting_types_list_service, update_copywriting_type_service,
    delete_copywriting_type_service, search_copywriting_types_service
)
from utils.auth import get_current_admin, get_current_user, get_current_admin_or_user
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/copywriting_types", tags=["文案类型管理"])

@router.post("/create", response_model=CopywritingTypeOut, summary="创建文案类型")
def create_copywriting_type(
    copywriting_type_data: CopywritingTypeCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    创建文案类型接口
    - name: 文案类型名称
    - prompt: 提示词
    - template: 模板
    - description: 描述
    - template_type: 模板类型（0-文案生成模板，1-文案优化模板）
    - icon: 图标
    """
    logger.info(f"尝试创建文案类型: {copywriting_type_data.name}")
    copywriting_type_data.updated_admin_uid = current_admin.uid
    result = create_copywriting_type_service(db, copywriting_type_data)
    logger.info(f"文案类型创建成功: {result.name}")
    return result

@router.get("/get/{uid}", response_model=CopywritingTypeOut, summary="获取指定UID的文案类型")
def get_copywriting_type(
    uid: str = Path(..., description="文案类型UID"),
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_admin_or_user)
):
    """
    根据UID获取文案类型信息
    """
    logger.info(f"查询文案类型: UID={uid}")
    return get_copywriting_type_service(db, uid)

@router.get("/list", response_model=CopywritingTypeListResponse, summary="获取未删除的所有文案类型")
def get_copywriting_types_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_admin_or_user)
):
    """
    获取文案类型列表（未删除）
    """
    logger.info(f"获取文案类型列表: page={page}, page_size={page_size}")
    skip = (page - 1) * page_size
    return get_copywriting_types_list_service(db, skip, page_size)

@router.post("/search", response_model=CopywritingTypeListResponse, summary="根据条件搜索文案类型")
def search_copywriting_types(
    search_params: CopywritingTypeSearchParams,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    根据多个条件搜索文案类型
    
    - name: 名称（模糊搜索）
    - template_type: 模板类型（0-文案生成模板，1-文案优化模板）
    - is_del: 是否删除（0-未删除，1-已删除）
    - start_time: 创建时间开始
    - end_time: 创建时间结束
    """
    logger.info(f"搜索文案类型: {search_params.model_dump()}")
    skip = (page - 1) * page_size
    return search_copywriting_types_service(db, search_params, skip, page_size)

@router.post("/update/{uid}", response_model=CopywritingTypeOut, summary="更新指定UID的文案类型")
def update_copywriting_type(
    uid: str = Path(..., description="文案类型UID"),
    copywriting_type_data: CopywritingTypeUpdate = Body(...),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    更新文案类型信息
    
    - uid: 文案类型UID
    - name: 文案类型名称（可选）
    - prompt: 提示词（可选）
    - template: 模板（可选）
    - description: 描述（可选）
    - template_type: 模板类型（可选，0-文案生成模板，1-文案优化模板）
    - icon: 图标（可选）
    """
    logger.info(f"尝试更新文案类型: UID={uid}")
    # 设置更新管理员UID
    copywriting_type_data.updated_admin_uid = current_admin.uid
    result = update_copywriting_type_service(db, uid, copywriting_type_data)
    logger.info(f"文案类型更新成功: {result.name}")
    return result

@router.post("/delete/{uid}", summary="删除指定UID的文案类型")
def delete_copywriting_type(
    uid: str = Path(..., description="文案类型UID"),
    delete_data: CopywritingTypeDelete = Body(...),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    软删除文案类型
    
    - updated_admin_uid: 更新管理员ID
    """
    logger.info(f"尝试删除文案类型: UID={uid}")
    result = delete_copywriting_type_service(db, uid, current_admin.uid)
    logger.info(f"文案类型删除成功: UID={uid}")
    return result