from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.knowledge import (
    KnowledgeCreate, KnowledgeUpdate, KnowledgeOut, KnowledgeSearchParams,
    KnowledgeListResponse, PaginationParams
)
from modules.knowledge.controller import (
    create_knowledge_item, get_knowledge_info, get_knowledge_info_by_uid, update_knowledge_info,
    delete_knowledge_item, get_knowledges_list, search_knowledges_list,
    batch_delete_knowledges_items, get_knowledge_statistics
)
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/knowledge", tags=["知识库管理"])

@router.post("/", response_model=KnowledgeOut, summary="创建知识库")
def create_knowledge(
    knowledge_data: KnowledgeCreate,
    db: Session = Depends(get_db)
):
    """
    创建知识库接口
    
    - **name**: 名称（必填，最大50字符）
    - **content**: 内容（必填，最大255字符）
    - **description**: 描述（必填，最大255字符）
    - **updated_admin_uid**: 更新管理员ID（必填）
    """
    return create_knowledge_item(db, knowledge_data)

@router.get("/{knowledge_id}", response_model=KnowledgeOut, summary="获取知识库信息")
def get_knowledge(
    knowledge_id: int = Path(..., description="知识库ID"),
    db: Session = Depends(get_db)
):
    """
    根据ID获取知识库信息
    
    - **knowledge_id**: 知识库ID
    """
    return get_knowledge_info(db, knowledge_id)

@router.get("/uid/{uid}", response_model=KnowledgeOut, summary="根据UID获取知识库信息")
def get_knowledge_by_uid(
    uid: str = Path(..., description="知识库UID"),
    db: Session = Depends(get_db)
):
    """
    根据UID获取知识库信息
    
    - **uid**: 知识库UID
    """
    return get_knowledge_info_by_uid(db, uid)

@router.put("/{knowledge_id}", response_model=KnowledgeOut, summary="更新知识库信息")
def update_knowledge(
    knowledge_id: int = Path(..., description="知识库ID"),
    update_data: KnowledgeUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """
    更新知识库信息
    
    - **knowledge_id**: 知识库ID
    - **name**: 名称（可选）
    - **content**: 内容（可选）
    - **description**: 描述（可选）
    - **updated_admin_uid**: 更新管理员ID（必填）
    """
    return update_knowledge_info(db, knowledge_id, update_data)

@router.delete("/{knowledge_id}", summary="删除知识库")
def delete_knowledge(
    knowledge_id: int = Path(..., description="知识库ID"),
    db: Session = Depends(get_db)
):
    """
    删除知识库（软删除）
    
    - **knowledge_id**: 知识库ID
    """
    return delete_knowledge_item(db, knowledge_id)

@router.get("/", response_model=KnowledgeListResponse, summary="获取知识库列表")
def get_knowledges(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取知识库列表
    
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    """
    skip = (page - 1) * page_size
    pagination = PaginationParams(skip=skip, limit=page_size)
    return get_knowledges_list(db, pagination)

@router.get("/search/", response_model=KnowledgeListResponse, summary="搜索知识库")
def search_knowledges(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    name: Optional[str] = Query(None, description="名称（模糊搜索）"),
    content: Optional[str] = Query(None, description="内容（模糊搜索）"),
    description: Optional[str] = Query(None, description="描述（模糊搜索）"),
    updated_admin_uid: Optional[str] = Query(None, description="更新管理员ID"),
    start_time: Optional[datetime] = Query(None, description="创建开始时间"),
    end_time: Optional[datetime] = Query(None, description="创建结束时间"),
    db: Session = Depends(get_db)
):
    """
    搜索知识库
    
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    - **name**: 名称（模糊搜索）
    - **content**: 内容（模糊搜索）
    - **description**: 描述（模糊搜索）
    - **updated_admin_uid**: 更新管理员ID
    - **start_time**: 创建开始时间
    - **end_time**: 创建结束时间
    """
    skip = (page - 1) * page_size
    pagination = PaginationParams(skip=skip, limit=page_size)
    search_params = KnowledgeSearchParams(
        name=name,
        content=content,
        description=description,
        updated_admin_uid=updated_admin_uid,
        start_time=start_time,
        end_time=end_time
    )
    return search_knowledges_list(db, search_params, pagination)

@router.delete("/batch/", summary="批量删除知识库")
def batch_delete_knowledges(
    knowledge_ids: List[int] = Body(..., description="知识库ID列表"),
    db: Session = Depends(get_db)
):
    """
    批量删除知识库（软删除）
    
    - **knowledge_ids**: 知识库ID列表
    """
    return batch_delete_knowledges_items(db, knowledge_ids)

@router.get("/stats/overview", summary="知识库统计概览")
def get_knowledge_stats(
    db: Session = Depends(get_db)
):
    """
    获取知识库统计概览
    
    返回知识库的总数量和今日新增数量
    """
    return get_knowledge_statistics(db)