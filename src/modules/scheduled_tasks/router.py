from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.scheduled_tasks import (
    ScheduledTaskCreate, ScheduledTaskEdit, ScheduledTaskDelete,
    ScheduledTaskOut, ScheduledTaskListResponse, ScheduledTaskSearchParams
)
from .controller import (
    create_scheduled_task_service, get_scheduled_task_service, get_scheduled_tasks_service,
    update_scheduled_task_service, delete_scheduled_task_service, search_scheduled_tasks_service,
    toggle_task_system_level_service
)
from utils.auth import get_current_user, get_current_admin, get_current_admin_or_user
from db.user import User
from db.admin import Admin
from typing import Union
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["定时任务"], prefix="/tasks")

@router.get("/get/{uid}", response_model=ScheduledTaskListResponse, summary="根据用户uid获取任务列表")
def get_tasks_by_user(
    uid: str,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_user: Union[User, Admin] = Depends(get_current_admin_or_user)
):
    """
    根据用户uid获取任务列表
    - 管理员可获取任何用户的任务列表
    - 普通用户只能获取自己的任务列表
    """
    logger.info(f"获取用户 {uid} 的定时任务列表")
    
    # 判断当前用户是否为管理员
    is_admin = hasattr(current_user, '__tablename__') and current_user.__tablename__ == 'admins'
    
    # 权限检查：普通用户只能查看自己的任务
    if not is_admin and current_user.uid != uid:
        logger.warning(f"用户 {current_user.uid} 尝试访问用户 {uid} 的任务列表")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问其他用户的任务列表"
        )
    
    return get_scheduled_tasks_service(db, uid, is_admin, skip, limit)

@router.post("/create", response_model=ScheduledTaskOut, summary="用户创建定时任务")
def create_task(
    task_data: ScheduledTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """用户创建定时任务接口"""
    logger.info(f"用户 {current_user.username} 创建定时任务: {task_data.name}")
    return create_scheduled_task_service(db, task_data, current_user.uid)

@router.post("/edit", response_model=ScheduledTaskOut, summary="用户修改定时任务")
def edit_task(
    task_data: ScheduledTaskEdit,
    db: Session = Depends(get_db),
    current_user: Union[User, Admin] = Depends(get_current_admin_or_user)
):
    """用户修改定时任务接口"""
    logger.info(f"用户 {current_user.username} 修改定时任务: {task_data.uid}")
    
    # 判断当前用户是否为管理员
    is_admin = hasattr(current_user, '__tablename__') and current_user.__tablename__ == 'admins'
    
    return update_scheduled_task_service(db, task_data, current_user.uid, is_admin)

@router.post("/del", summary="用户删除定时任务")
def delete_task(
    task_data: ScheduledTaskDelete,
    db: Session = Depends(get_db),
    current_user: Union[User, Admin] = Depends(get_current_admin_or_user)
):
    """用户删除定时任务接口"""
    logger.info(f"用户 {current_user.username} 删除定时任务: {task_data.uid}")
    
    # 判断当前用户是否为管理员
    is_admin = hasattr(current_user, '__tablename__') and current_user.__tablename__ == 'admins'
    
    return delete_scheduled_task_service(db, task_data, current_user.uid, is_admin)

# 额外的管理员专用接口
@router.get("/admin/list", response_model=ScheduledTaskListResponse, summary="管理员获取所有任务列表")
def get_all_tasks_admin(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """管理员获取所有任务列表接口"""
    logger.info(f"管理员 {current_admin.username} 获取所有定时任务列表")
    return get_scheduled_tasks_service(db, current_admin.uid, True, skip, limit)

@router.get("/detail/{task_uid}", response_model=ScheduledTaskOut, summary="获取任务详情")
def get_task_detail(
    task_uid: str,
    db: Session = Depends(get_db),
    current_user: Union[User, Admin] = Depends(get_current_admin_or_user)
):
    """获取任务详情接口"""
    logger.info(f"用户 {current_user.username} 获取任务详情: {task_uid}")
    
    # 判断当前用户是否为管理员
    is_admin = hasattr(current_user, '__tablename__') and current_user.__tablename__ == 'admins'
    
    return get_scheduled_task_service(db, task_uid, current_user.uid, is_admin)

@router.post("/search", response_model=ScheduledTaskListResponse, summary="搜索定时任务")
def search_tasks(
    search_params: ScheduledTaskSearchParams,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_user: Union[User, Admin] = Depends(get_current_admin_or_user)
):
    """搜索定时任务接口"""
    logger.info(f"用户 {current_user.username} 搜索定时任务")
    
    # 判断当前用户是否为管理员
    is_admin = hasattr(current_user, '__tablename__') and current_user.__tablename__ == 'admins'
    
    return search_scheduled_tasks_service(db, search_params, current_user.uid, is_admin, skip, limit)

# 管理员专用的任务管理接口


@router.post("/toggle/{task_uid}", response_model=ScheduledTaskOut, summary="切换任务启用状态")
def toggle_task_status(
    task_uid: str,
    db: Session = Depends(get_db),
    current_user_or_admin = Depends(get_current_admin_or_user)
):
    """切换任务启用状态接口（用户只能切换自己的任务，管理员可以切换所有任务）"""
    is_admin = hasattr(current_user_or_admin, 'role') and current_user_or_admin.role == 'admin'
    user_type = "管理员" if is_admin else "用户"
    username = current_user_or_admin.username
    
    logger.info(f"{user_type} {username} 切换任务状态: {task_uid}")
    
    # 获取当前任务状态
    task = get_scheduled_task_service(db, task_uid, current_user_or_admin.uid, is_admin)
    
    # 切换启用状态
    from schemas.scheduled_tasks import ScheduledTaskEdit
    edit_data = ScheduledTaskEdit(
        uid=task_uid,
        is_enable=1 - task.is_enable  # 0变1，1变0
    )
    
    return update_scheduled_task_service(db, edit_data, current_user_or_admin.uid, is_admin)


@router.post("/toggle-system/{task_uid}", response_model=ScheduledTaskOut, summary="切换任务系统级状态")
def toggle_task_system_level(
    task_uid: str,
    db: Session = Depends(get_db),
    current_user_or_admin = Depends(get_current_admin_or_user)
):
    """切换任务系统级状态接口（用户只能切换自己的任务，管理员可以切换所有任务）"""
    is_admin = hasattr(current_user_or_admin, 'role') and current_user_or_admin.role == 'admin'
    user_type = "管理员" if is_admin else "用户"
    username = current_user_or_admin.username
    
    logger.info(f"{user_type} {username} 切换任务系统级状态: {task_uid}")
    
    return toggle_task_system_level_service(db, task_uid, current_user_or_admin.uid, is_admin)