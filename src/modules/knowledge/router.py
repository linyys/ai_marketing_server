from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.knowledge import (
    KnowledgeCreate, KnowledgeUpdate, KnowledgeOut, KnowledgeListResponse,
    KnowledgeSearchParams, PaginationParams, KnowledgeUidListResponse
)
from modules.knowledge.controller import (
    create_knowledge_service, get_knowledge_service, get_knowledges_list_service,
    get_user_knowledges_service, update_knowledge_service, delete_knowledge_service,
    search_knowledges_service, get_knowledge_uids_by_robot_service
)
from utils.auth import get_current_user, get_current_admin, get_current_admin_or_user
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["知识库"], prefix="/knowledge")

@router.get("/list", response_model=KnowledgeListResponse, summary="获取所有知识库列表")
def get_knowledges_list(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """获取所有知识库列表接口（仅管理员可访问）"""
    logger.info(f"管理员 {current_admin.username} 请求知识库列表")
    return get_knowledges_list_service(db, skip, limit, is_admin=True)

@router.get("/list/{uid}", response_model=KnowledgeListResponse, summary="获取指定用户的知识库列表")
def get_user_knowledges(
    uid: str,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    """获取指定用户的知识库列表接口（管理员或本人可访问）"""
    # 检查权限：管理员或本人
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    current_user_uid = current_user.uid
    
    if is_admin:
        logger.info(f"管理员 {current_user.username} 请求用户 {uid} 的知识库列表")
    else:
        # 非管理员，检查是否为本人
        if uid != current_user_uid:
            logger.warning(f"用户 {current_user_uid} 尝试访问其他用户的知识库: {uid}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限访问其他用户的知识库"
            )
        logger.info(f"用户 {current_user_uid} 请求自己的知识库列表")
    
    return get_user_knowledges_service(
        db, uid, skip, limit, current_user_uid, is_admin
    )

@router.get("/get/{uid}", response_model=KnowledgeOut, summary="获取指定知识库详情")
def get_knowledge(
    uid: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    """获取指定知识库详情接口（管理员或所有者可访问，公共知识库所有人可见）"""
    # 检查权限：管理员或知识库所有者
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    current_user_uid = current_user.uid
    
    if is_admin:
        logger.info(f"管理员 {current_user.username} 请求知识库详情: {uid}")
    else:
        logger.info(f"用户 {current_user_uid} 请求知识库详情: {uid}")
    
    return get_knowledge_service(db, uid, current_user_uid, is_admin)

@router.post("/search", response_model=KnowledgeListResponse, summary="搜索知识库")
def search_knowledges(
    search_params: KnowledgeSearchParams,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    """搜索知识库接口（管理员可搜索所有，用户只能搜索自己可访问的）"""
    # 检查权限：管理员或普通用户
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    current_user_uid = current_user.uid
    
    if is_admin:
        logger.info(f"管理员 {current_user.username} 搜索知识库")
    else:
        logger.info(f"用户 {current_user_uid} 搜索自己的知识库")
    
    return search_knowledges_service(
        db, search_params, skip, limit, current_user_uid, is_admin
    )

@router.post("/create", response_model=KnowledgeOut, summary="创建知识库")
def create_knowledge(
    knowledge_data: KnowledgeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    """创建知识库接口（管理员和用户都可创建）"""
    # 检查权限：管理员或普通用户
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    
    if is_admin:
        from_user = None  # 管理员创建的知识库为公共知识库
        logger.info(f"管理员 {current_user.username} 创建知识库: {knowledge_data.name}")
    else:
        from_user = current_user.uid  # 用户创建的知识库为私有知识库
        logger.info(f"用户 {current_user.uid} 创建知识库: {knowledge_data.name}")
    
    return create_knowledge_service(db, knowledge_data, from_user, is_admin)

@router.post("/update", response_model=KnowledgeOut, summary="更新知识库")
def update_knowledge(
    uid: str,
    knowledge_data: KnowledgeUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    """更新知识库接口（管理员或所有者可更新）"""
    # 检查权限：管理员或知识库所有者
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    current_user_uid = current_user.uid
    
    if is_admin:
        logger.info(f"管理员 {current_user.username} 更新知识库 {uid}")
    else:
        logger.info(f"用户 {current_user_uid} 更新知识库 {uid}")
    
    return update_knowledge_service(db, uid, knowledge_data, current_user_uid, is_admin)

@router.post("/delete", summary="删除知识库")
def delete_knowledge(
    uid: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    """删除知识库接口（管理员或所有者可删除）"""
    # 检查权限：管理员或知识库所有者
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    current_user_uid = current_user.uid
    
    if is_admin:
        logger.info(f"管理员 {current_user.username} 删除知识库 {uid}")
    else:
        logger.info(f"用户 {current_user_uid} 删除知识库 {uid}")
    
    return delete_knowledge_service(db, uid, current_user_uid, is_admin)

@router.get("/get_by_robot/{uid}", response_model=KnowledgeUidListResponse, summary="根据机器人UID获取知识库UID列表")
def get_knowledge_uids_by_robot(
    uid: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    """根据机器人UID获取关联的知识库ID列表接口（管理员和用户都可访问）"""
    # 检查权限：管理员或普通用户
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    current_user_uid = current_user.uid
    
    if is_admin:
        logger.info(f"管理员 {current_user.username} 请求机器人 {uid} 的知识库ID列表")
    else:
        logger.info(f"用户 {current_user_uid} 请求机器人 {uid} 的知识库ID列表")
    
    return get_knowledge_uids_by_robot_service(db, uid, current_user_uid, is_admin)
