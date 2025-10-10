from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from crud.scheduled_tasks import (
    create_scheduled_task, get_scheduled_task_by_uid, get_scheduled_tasks_by_user,
    get_all_scheduled_tasks, get_scheduled_tasks_count_by_user, get_all_scheduled_tasks_count,
    update_scheduled_task, delete_scheduled_task, search_scheduled_tasks
)
from schemas.scheduled_tasks import (
    ScheduledTaskCreate, ScheduledTaskUpdate, ScheduledTaskEdit, ScheduledTaskDelete,
    ScheduledTaskOut, ScheduledTaskListResponse, ScheduledTaskSearchParams, PlatformEnum
)
from typing import List, Union
import logging

logger = logging.getLogger(__name__)

def create_scheduled_task_service(
    db: Session, 
    task_data: ScheduledTaskCreate, 
    from_user: str
) -> ScheduledTaskOut:
    """创建定时任务服务"""
    try:
        # 验证平台参数
        if not PlatformEnum.is_valid_platform(task_data.platform):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的平台参数"
            )
        
        task = create_scheduled_task(
            db=db,
            from_user=from_user,
            name=task_data.name,
            content=task_data.content,
            description=task_data.description,
            platform=task_data.platform,
            time_cron=task_data.time_cron,
            is_system=task_data.is_system or 0,
            one_time=task_data.one_time or 0
        )
        return ScheduledTaskOut.model_validate(task)
    except ValueError as e:
        logger.warning(f"创建定时任务失败 - 数据验证错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"创建定时任务失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建定时任务失败，请稍后重试"
        )

def get_scheduled_tasks_service(
    db: Session, 
    user_uid: str, 
    is_admin: bool = False,
    skip: int = 0, 
    limit: int = 20
) -> ScheduledTaskListResponse:
    """获取定时任务列表服务"""
    try:
        if is_admin:
            # 管理员可以获取所有任务
            tasks = get_all_scheduled_tasks(db, skip, limit)
            total = get_all_scheduled_tasks_count(db)
        else:
            # 普通用户只能获取自己的任务
            tasks = get_scheduled_tasks_by_user(db, user_uid, skip, limit)
            total = get_scheduled_tasks_count_by_user(db, user_uid)
        
        task_list = [ScheduledTaskOut.model_validate(task) for task in tasks]
        
        return ScheduledTaskListResponse(
            total=total,
            items=task_list,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"获取定时任务列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取定时任务列表失败，请稍后重试"
        )

def get_scheduled_task_service(
    db: Session, 
    task_uid: str, 
    current_user_uid: str, 
    is_admin: bool = False
) -> ScheduledTaskOut:
    """获取单个定时任务服务"""
    try:
        task = get_scheduled_task_by_uid(db, task_uid)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="定时任务不存在"
            )
        
        # 权限检查：管理员可以查看所有任务，普通用户只能查看自己的任务
        if not is_admin and task.from_user != current_user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限访问该定时任务"
            )
        
        return ScheduledTaskOut.model_validate(task)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取定时任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取定时任务失败，请稍后重试"
        )

def update_scheduled_task_service(
    db: Session, 
    task_data: ScheduledTaskEdit, 
    current_user_uid: str, 
    is_admin: bool = False
) -> ScheduledTaskOut:
    """更新定时任务服务"""
    try:
        # 检查任务是否存在
        existing_task = get_scheduled_task_by_uid(db, task_data.uid)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="定时任务不存在"
            )
        
        # 权限检查：管理员可以修改所有任务，普通用户只能修改自己的任务
        if not is_admin and existing_task.from_user != current_user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改该定时任务"
            )
        
        # 验证平台参数
        if task_data.platform is not None and not PlatformEnum.is_valid_platform(task_data.platform):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的平台参数"
            )
        
        updated_task = update_scheduled_task(
            db=db,
            uid=task_data.uid,
            name=task_data.name,
            content=task_data.content,
            description=task_data.description,
            platform=task_data.platform,
            time_cron=task_data.time_cron
        )
        
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="定时任务不存在"
            )
        
        return ScheduledTaskOut.model_validate(updated_task)
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"更新定时任务失败 - 数据验证错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"更新定时任务失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新定时任务失败，请稍后重试"
        )

def delete_scheduled_task_service(
    db: Session, 
    task_data: ScheduledTaskDelete, 
    current_user_uid: str, 
    is_admin: bool = False
) -> dict:
    """删除定时任务服务"""
    try:
        # 检查任务是否存在
        existing_task = get_scheduled_task_by_uid(db, task_data.uid)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="定时任务不存在"
            )
        
        # 权限检查：管理员可以删除所有任务，普通用户只能删除自己的任务
        if not is_admin and existing_task.from_user != current_user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限删除该定时任务"
            )
        
        success = delete_scheduled_task(db, task_data.uid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="定时任务不存在"
            )
        
        return {"message": "定时任务删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除定时任务失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除定时任务失败，请稍后重试"
        )

def search_scheduled_tasks_service(
    db: Session,
    search_params: ScheduledTaskSearchParams,
    current_user_uid: str,
    is_admin: bool = False,
    skip: int = 0,
    limit: int = 20
) -> ScheduledTaskListResponse:
    """搜索定时任务服务"""
    try:
        # 验证平台参数
        if search_params.platform is not None and not PlatformEnum.is_valid_platform(search_params.platform):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的平台参数"
            )
        
        # 如果不是管理员，只能搜索自己的任务
        from_user = None if is_admin else current_user_uid
        
        tasks, total = search_scheduled_tasks(
            db=db,
            name=search_params.name,
            platform=search_params.platform,
            one_time=search_params.one_time,
            from_user=from_user,
            skip=skip,
            limit=limit
        )
        
        task_list = [ScheduledTaskOut.model_validate(task) for task in tasks]
        
        return ScheduledTaskListResponse(
            total=total,
            items=task_list,
            skip=skip,
            limit=limit
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索定时任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="搜索定时任务失败，请稍后重试"
        )


def toggle_task_system_level_service(
    db: Session,
    task_uid: str,
    current_user_uid: str,
    is_admin: bool = False
) -> ScheduledTaskOut:
    """切换任务系统级状态的业务逻辑（用户只能切换自己的任务，管理员可以切换所有任务）"""
    try:
        
        # 获取任务信息（使用现有的权限验证逻辑）
        task = get_scheduled_task_by_uid(db, task_uid)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        # 权限验证：用户只能操作自己的任务，管理员可以操作所有任务
        if not is_admin and task.from_user != current_user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您只能操作自己的任务"
            )
        
        # 切换系统级状态
        new_system_status = 1 - task.is_system  # 0变1，1变0
        
        # 构造更新数据
        edit_data = ScheduledTaskEdit(
            uid=task_uid,
            is_system=new_system_status
        )
        
        # 更新任务
        updated_task = update_scheduled_task(
            db=db,
            uid=task_uid,
            name=edit_data.name,
            content=edit_data.content,
            description=edit_data.description,
            platform=edit_data.platform,
            time_cron=edit_data.time_cron,
            is_system=edit_data.is_system
        )
        
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在或更新失败"
            )
        
        system_status_text = "系统通知" if new_system_status else "普通任务"
        user_type = "管理员" if is_admin else "用户"
        logger.info(f"{user_type} {current_user_uid} 将任务 {task_uid} 切换为{system_status_text}")
        
        return ScheduledTaskOut.model_validate(updated_task)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换任务系统级状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="切换任务系统级状态失败，请稍后重试"
        )