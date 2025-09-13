from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from crud.copywriting_types import (
    create_copywriting_type, get_copywriting_type_by_uid, get_copywriting_types,
    get_copywriting_types_count, update_copywriting_type, soft_delete_copywriting_type,
    search_copywriting_types
)
from schemas.copywriting_types import (
    CopywritingTypeCreate, CopywritingTypeUpdate, CopywritingTypeOut,
    CopywritingTypeSearchParams, CopywritingTypeListResponse
)
from typing import List
import logging

logger = logging.getLogger(__name__)

def create_copywriting_type_service(
    db: Session,
    copywriting_type_data: CopywritingTypeCreate
) -> CopywritingTypeOut:
    """创建文案类型服务"""
    try:
        copywriting_type = create_copywriting_type(
            db=db,
            name=copywriting_type_data.name,
            prompt=copywriting_type_data.prompt,
            template=copywriting_type_data.template,
            description=copywriting_type_data.description,
            icon=copywriting_type_data.icon,
            updated_admin_uid=copywriting_type_data.updated_admin_uid
        )
        return CopywritingTypeOut.model_validate(copywriting_type)
    except ValueError as e:
        logger.warning(f"创建文案类型失败 - 数据验证错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"创建文案类型失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建文案类型失败，请稍后重试"
        )

def get_copywriting_type_service(db: Session, uid: str) -> CopywritingTypeOut:
    """获取文案类型服务"""
    try:
        copywriting_type = get_copywriting_type_by_uid(db, uid)
        if not copywriting_type:
            logger.warning(f"文案类型不存在: UID={uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文案类型不存在"
            )
        return CopywritingTypeOut.model_validate(copywriting_type)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文案类型失败: UID={uid}, 错误={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取文案类型信息失败"
        )

def get_copywriting_types_list_service(
    db: Session,
    skip: int = 0,
    limit: int = 20
) -> CopywritingTypeListResponse:
    """获取文案类型列表服务"""
    try:
        copywriting_types = get_copywriting_types(db, skip, limit)
        total = get_copywriting_types_count(db)
        
        items = [CopywritingTypeOut.model_validate(ct) for ct in copywriting_types]
        
        return CopywritingTypeListResponse(
            total=total,
            items=items,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"获取文案类型列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取文案类型列表失败"
        )

def update_copywriting_type_service(
    db: Session,
    uid: str,
    copywriting_type_data: CopywritingTypeUpdate
) -> CopywritingTypeOut:
    """更新文案类型服务"""
    try:
        copywriting_type = update_copywriting_type(
            db=db,
            uid=uid,
            updated_admin_uid=copywriting_type_data.updated_admin_uid,
            name=copywriting_type_data.name,
            prompt=copywriting_type_data.prompt,
            template=copywriting_type_data.template,
            description=copywriting_type_data.description,
            icon=copywriting_type_data.icon
        )
        
        if not copywriting_type:
            logger.warning(f"文案类型不存在: UID={uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文案类型不存在"
            )
        
        return CopywritingTypeOut.model_validate(copywriting_type)
    except ValueError as e:
        logger.warning(f"更新文案类型失败 - 数据验证错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新文案类型失败: UID={uid}, 错误={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新文案类型失败，请稍后重试"
        )

def delete_copywriting_type_service(
    db: Session,
    uid: str,
    updated_admin_uid: str
) -> dict:
    """删除文案类型服务"""
    try:
        success = soft_delete_copywriting_type(db, uid, updated_admin_uid)
        if not success:
            logger.warning(f"文案类型不存在: UID={uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文案类型不存在"
            )
        
        return {"message": "文案类型删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文案类型失败: UID={uid}, 错误={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除文案类型失败，请稍后重试"
        )

def search_copywriting_types_service(
    db: Session,
    search_params: CopywritingTypeSearchParams,
    skip: int = 0,
    limit: int = 20
) -> CopywritingTypeListResponse:
    """搜索文案类型服务"""
    try:
        copywriting_types, total = search_copywriting_types(
            db=db,
            name=search_params.name,
            is_del=search_params.is_del,
            start_time=search_params.start_time,
            end_time=search_params.end_time,
            skip=skip,
            limit=limit
        )
        
        items = [CopywritingTypeOut.model_validate(ct) for ct in copywriting_types]
        
        return CopywritingTypeListResponse(
            total=total,
            items=items,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"搜索文案类型失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="搜索文案类型失败"
        )