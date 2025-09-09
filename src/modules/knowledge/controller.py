from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from crud.knowledge import (
    create_knowledge, get_knowledge_by_id, get_knowledge_by_uid, get_knowledges, get_knowledges_count,
    update_knowledge, soft_delete_knowledge, search_knowledges, batch_delete_knowledges, get_knowledge_stats
)
from schemas.knowledge import (
    KnowledgeCreate, KnowledgeUpdate, KnowledgeOut, KnowledgeSearchParams, 
    KnowledgeListResponse, PaginationParams
)
from typing import List
import logging

logger = logging.getLogger(__name__)

def create_knowledge_item(db: Session, knowledge_data: KnowledgeCreate) -> KnowledgeOut:
    """创建知识库"""
    try:
        knowledge = create_knowledge(db, knowledge_data)
        return KnowledgeOut.from_orm(knowledge)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating knowledge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建知识库失败"
        )

def get_knowledge_info(db: Session, knowledge_id: int) -> KnowledgeOut:
    """获取知识库信息"""
    knowledge = get_knowledge_by_id(db, knowledge_id)
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )
    return KnowledgeOut.from_orm(knowledge)

def get_knowledge_info_by_uid(db: Session, uid: str) -> KnowledgeOut:
    """根据UID获取知识库信息"""
    knowledge = get_knowledge_by_uid(db, uid)
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )
    return KnowledgeOut.from_orm(knowledge)

def update_knowledge_info(db: Session, knowledge_id: int, update_data: KnowledgeUpdate) -> KnowledgeOut:
    """更新知识库信息"""
    try:
        knowledge = update_knowledge(db, knowledge_id, update_data)
        if not knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在"
            )
        return KnowledgeOut.from_orm(knowledge)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating knowledge {knowledge_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新知识库失败"
        )

def delete_knowledge_item(db: Session, knowledge_id: int) -> dict:
    """删除知识库"""
    try:
        success = soft_delete_knowledge(db, knowledge_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在"
            )
        return {"message": "知识库删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting knowledge {knowledge_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除知识库失败"
        )

def get_knowledges_list(db: Session, pagination: PaginationParams) -> KnowledgeListResponse:
    """获取知识库列表"""
    try:
        knowledges = get_knowledges(db, pagination.skip, pagination.limit)
        total = get_knowledges_count(db)
        
        knowledge_outs = [KnowledgeOut.from_orm(knowledge) for knowledge in knowledges]
        
        return KnowledgeListResponse(
            total=total,
            items=knowledge_outs,
            skip=pagination.skip,
            limit=pagination.limit
        )
    except Exception as e:
        logger.error(f"Error getting knowledges list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取知识库列表失败"
        )

def search_knowledges_list(db: Session, search_params: KnowledgeSearchParams, pagination: PaginationParams) -> KnowledgeListResponse:
    """搜索知识库列表"""
    try:
        knowledges, total = search_knowledges(db, search_params, pagination.skip, pagination.limit)
        
        knowledge_outs = [KnowledgeOut.from_orm(knowledge) for knowledge in knowledges]
        
        return KnowledgeListResponse(
            total=total,
            items=knowledge_outs,
            skip=pagination.skip,
            limit=pagination.limit
        )
    except Exception as e:
        logger.error(f"Error searching knowledges: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="搜索知识库失败"
        )

def batch_delete_knowledges_items(db: Session, knowledge_ids: List[int]) -> dict:
    """批量删除知识库"""
    try:
        if not knowledge_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请提供要删除的知识库ID列表"
            )
        
        success = batch_delete_knowledges(db, knowledge_ids)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="批量删除知识库失败"
            )
        
        return {
            "message": f"成功删除 {len(knowledge_ids)} 个知识库",
            "deleted_count": len(knowledge_ids)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error batch deleting knowledges {knowledge_ids}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量删除知识库失败"
        )

def get_knowledge_statistics(db: Session) -> dict:
    """获取知识库统计信息"""
    try:
        stats = get_knowledge_stats(db)
        return {
            "total_count": stats["total_count"],
            "today_count": stats["today_count"],
            "message": "统计信息获取成功"
        }
    except Exception as e:
        logger.error(f"Error getting knowledge statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计信息失败"
        )