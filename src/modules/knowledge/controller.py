from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from crud.knowledge import (
    create_knowledge,
    get_knowledge_by_uid,
    get_knowledges,
    get_knowledges_count,
    get_knowledges_by_user,
    get_knowledges_by_user_count,
    update_knowledge,
    delete_knowledge,
    search_knowledges,
    search_user_accessible_knowledges,
    get_knowledge_uids_by_robot_uid,
)
from schemas.knowledge import (
    KnowledgeCreate,
    KnowledgeUpdate,
    KnowledgeOut,
    KnowledgeListResponse,
    KnowledgeSearchParams,
    PaginationParams,
    KnowledgeUidListResponse,
)
from typing import List
import logging

logger = logging.getLogger(__name__)


def create_knowledge_service(
    db: Session,
    knowledge_data: KnowledgeCreate,
    from_user: str = None,
    is_admin: bool = False,
) -> KnowledgeOut:
    """
    创建知识库服务
    """
    try:
        # 管理员创建的知识库默认为公共知识库（from_user为空）
        actual_from_user = None if is_admin else from_user

        db_knowledge = create_knowledge(
            db=db,
            name=knowledge_data.name,
            content=knowledge_data.content,
            description=knowledge_data.description,
            from_user=actual_from_user,
        )

        logger.info(f"知识库创建成功: {db_knowledge.uid}")
        return KnowledgeOut.model_validate(db_knowledge)

    except ValueError as e:
        logger.error(f"创建知识库失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"创建知识库异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建知识库失败"
        )


def get_knowledge_service(
    db: Session, uid: str, current_user_uid: str = None, is_admin: bool = False
) -> KnowledgeOut:
    """
    获取知识库详情服务
    """
    try:
        db_knowledge = get_knowledge_by_uid(db, uid)
        if not db_knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
            )

        # 权限检查
        if not is_admin:
            if (
                db_knowledge.from_user is not None
                and db_knowledge.from_user != current_user_uid
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问该知识库"
                )

        return KnowledgeOut.model_validate(db_knowledge)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取知识库异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取知识库失败"
        )


def get_knowledges_list_service(
    db: Session, skip: int = 0, limit: int = 20, is_admin: bool = False
) -> KnowledgeListResponse:
    """
    获取知识库列表服务（仅管理员）
    """
    try:
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="仅管理员可获取所有知识库列表",
            )

        knowledges = get_knowledges(db, skip=skip, limit=limit)
        total = get_knowledges_count(db)

        knowledge_list = [
            KnowledgeOut.model_validate(knowledge) for knowledge in knowledges
        ]

        return KnowledgeListResponse(
            total=total, items=knowledge_list, skip=skip, limit=limit
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取知识库列表异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取知识库列表失败",
        )


def get_user_knowledges_service(
    db: Session,
    user_uid: str,
    skip: int = 0,
    limit: int = 20,
    current_user_uid: str = None,
    is_admin: bool = False,
) -> KnowledgeListResponse:
    """
    获取指定用户的知识库列表服务
    """
    try:
        # 权限检查：管理员或本人
        if not is_admin and current_user_uid != user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问该用户的知识库"
            )

        knowledges = get_knowledges_by_user(db, user_uid, skip=skip, limit=limit)
        total = get_knowledges_by_user_count(db, user_uid)

        knowledge_list = [
            KnowledgeOut.model_validate(knowledge) for knowledge in knowledges
        ]

        return KnowledgeListResponse(
            total=total, items=knowledge_list, skip=skip, limit=limit
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户知识库列表异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户知识库列表失败",
        )


def update_knowledge_service(
    db: Session,
    uid: str,
    knowledge_data: KnowledgeUpdate,
    current_user_uid: str = None,
    is_admin: bool = False,
) -> KnowledgeOut:
    """
    更新知识库服务
    """
    try:
        db_knowledge = get_knowledge_by_uid(db, uid)
        if not db_knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
            )

        # 权限检查：管理员或所有者
        if not is_admin:
            if db_knowledge.from_user is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="公共知识库不可编辑"
                )
            if db_knowledge.from_user != current_user_uid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="无权限编辑该知识库"
                )

        updated_knowledge = update_knowledge(
            db=db,
            knowledge_uid=uid,
            name=knowledge_data.name,
            content=knowledge_data.content,
            description=knowledge_data.description,
        )

        if not updated_knowledge:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="更新知识库失败"
            )

        logger.info(f"知识库更新成功: {uid}")
        return KnowledgeOut.model_validate(updated_knowledge)

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"更新知识库失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"更新知识库异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新知识库失败"
        )


def delete_knowledge_service(
    db: Session, uid: str, current_user_uid: str = None, is_admin: bool = False
) -> dict:
    """
    删除知识库服务
    """
    try:
        db_knowledge = get_knowledge_by_uid(db, uid)
        if not db_knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
            )

        # 权限检查：管理员或所有者
        if not is_admin:
            if db_knowledge.from_user is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="公共知识库不可删除"
                )
            if db_knowledge.from_user != current_user_uid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="无权限删除该知识库"
                )

        success = delete_knowledge(db, uid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="删除知识库失败"
            )

        logger.info(f"知识库删除成功: {uid}")
        return {"message": "知识库删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除知识库异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除知识库失败"
        )


def search_knowledges_service(
    db: Session,
    search_params: KnowledgeSearchParams,
    skip: int = 0,
    limit: int = 20,
    current_user_uid: str = None,
    is_admin: bool = False,
) -> KnowledgeListResponse:
    """
    搜索知识库服务
    """
    try:
        if is_admin:
            # 管理员可以搜索所有知识库
            knowledges, total = search_knowledges(
                db=db,
                name=search_params.name,
                content=search_params.content,
                description=search_params.description,
                from_user=search_params.from_user,
                start_time=search_params.start_time,
                end_time=search_params.end_time,
                skip=skip,
                limit=limit,
            )
        else:
            # 普通用户只能搜索自己可访问的知识库
            knowledges, total = search_user_accessible_knowledges(
                db=db,
                user_uid=current_user_uid,
                name=search_params.name,
                content=search_params.content,
                description=search_params.description,
                start_time=search_params.start_time,
                end_time=search_params.end_time,
                skip=skip,
                limit=limit,
            )

        knowledge_list = [
            KnowledgeOut.model_validate(knowledge) for knowledge in knowledges
        ]

        return KnowledgeListResponse(
            total=total, items=knowledge_list, skip=skip, limit=limit
        )

    except Exception as e:
        logger.error(f"搜索知识库异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="搜索知识库失败"
        )

def get_knowledge_uids_by_robot_service(
    db: Session, robot_uid: str, current_user_uid: str = None, is_admin: bool = False
) -> KnowledgeUidListResponse:
    """
    根据机器人UID获取关联的知识库UID列表服务
    """
    try:
        logger.info(f"获取机器人 {robot_uid} 的知识库UID列表")
        
        knowledge_uids = get_knowledge_uids_by_robot_uid(db, robot_uid)
        
        return KnowledgeUidListResponse(knowledge_uids=knowledge_uids)
        
    except Exception as e:
        logger.error(f"获取机器人知识库ID列表异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="获取机器人知识库ID列表失败"
        )
