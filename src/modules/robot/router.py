from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from db.database import get_db
from utils.auth import get_current_user, get_current_admin, get_current_admin_or_user
from modules.robot.controller import (
    create_robot_service,
    get_robots_list_service,
    search_robots_service,
    get_robot_service,
    update_robot_service,
    delete_robot_service,
    add_robot_knowledge_service,
    add_robot_filter_service
)
from schemas.robot import (
    RobotCreate,
    RobotUpdate,
    RobotOut,
    RobotListResponse,
    RobotSearchParams,
    RobotDeleteRequest,
    RobotAddKnowledgeRequest,
    RobotFilterCreate,
    RobotFilterOut
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/robot", tags=["机器人管理"])

@router.post("/create", response_model=RobotOut, summary="创建机器人")
def create_robot(
    robot_data: RobotCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建机器人接口（用户权限）
    
    - **name**: 机器人名称
    - **reply_type**: 回复类型（0-评论 1-私信 2-群聊 3-私聊）
    - **platform**: 平台（0-微信 1-企业微信 3-抖音 4-小红书）
    - **login_type**: 登录类型（0-账号密码登录 1-扫码登录）
    - **description**: 描述
    - **account**: 账号（可选）
    - **password**: 密码（可选）
    """
    logger.info(f"用户 {current_user.uid} 请求创建机器人: {robot_data.name}")
    return create_robot_service(db, robot_data, current_user.uid)

@router.get("/get/list", response_model=RobotListResponse, summary="获取机器人列表")
def get_robots_list(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    """
    获取机器人列表接口
    
    - 管理员：可查询所有机器人
    - 用户：仅可查询自己的机器人
    """
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    current_user_uid = current_user.uid
    
    if is_admin:
        logger.info(f"管理员 {current_user.username} 请求机器人列表")
        return get_robots_list_service(db, skip, limit, is_admin=True)
    else:
        logger.info(f"用户 {current_user_uid} 请求自己的机器人列表")
        return get_robots_list_service(db, skip, limit, is_admin=False, user_uid=current_user_uid)

@router.post("/search", response_model=RobotListResponse, summary="搜索机器人")
def search_robots(
    search_params: RobotSearchParams,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    """
    搜索机器人接口
    
    - 管理员：可搜索所有机器人
    - 用户：仅可搜索自己的机器人
    
    搜索条件：
    - **name**: 机器人名称（模糊搜索）
    - **platform**: 平台
    - **is_enable**: 是否启用
    - **from_user_uid**: 用户UID（仅管理员可用）
    - **start_time**: 开始时间
    - **end_time**: 结束时间
    """
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    current_user_uid = current_user.uid
    
    if is_admin:
        logger.info(f"管理员 {current_user.username} 搜索机器人")
        return search_robots_service(db, search_params, skip, limit, is_admin=True)
    else:
        logger.info(f"用户 {current_user_uid} 搜索自己的机器人")
        return search_robots_service(db, search_params, skip, limit, is_admin=False, user_uid=current_user_uid)

@router.get("/get/{uid}", response_model=RobotOut, summary="获取单个机器人详情")
def get_robot(
    uid: str = Path(..., description="机器人UID"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    """
    获取单个机器人详情接口
    
    - 管理员：可查询任意机器人
    - 用户：仅可查询自己的机器人
    """
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    current_user_uid = current_user.uid
    
    if is_admin:
        logger.info(f"管理员 {current_user.username} 请求机器人详情: {uid}")
    else:
        logger.info(f"用户 {current_user_uid} 请求机器人详情: {uid}")
    
    return get_robot_service(db, uid, current_user_uid, is_admin)

@router.post("/update", response_model=RobotOut, summary="更新机器人")
def update_robot(
    uid: str,
    robot_data: RobotUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    """
    更新机器人接口
    
    - 管理员：可更新任意机器人
    - 用户：仅可更新自己的机器人
    
    可更新字段：
    - **name**: 机器人名称
    - **reply_type**: 回复类型
    - **account**: 账号
    - **password**: 密码
    - **platform**: 平台
    - **login_type**: 登录类型
    - **description**: 描述
    - **is_enable**: 是否启用
    """
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    current_user_uid = current_user.uid
    
    if is_admin:
        logger.info(f"管理员 {current_user.username} 更新机器人: {uid}")
    else:
        logger.info(f"用户 {current_user_uid} 更新机器人: {uid}")
    
    return update_robot_service(db, uid, robot_data, current_user_uid, is_admin)

@router.post("/delete", summary="删除机器人")
def delete_robot(
    delete_request: RobotDeleteRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_or_user)
):
    """
    删除机器人接口（软删除）
    
    - 管理员：可删除任意机器人
    - 用户：仅可删除自己的机器人
    """
    from db.admin import Admin
    is_admin = isinstance(current_user, Admin)
    current_user_uid = current_user.uid
    
    if is_admin:
        logger.info(f"管理员 {current_user.username} 删除机器人: {delete_request.uid}")
    else:
        logger.info(f"用户 {current_user_uid} 删除机器人: {delete_request.uid}")
    
    return delete_robot_service(db, delete_request, current_user_uid, is_admin)

@router.post("/add/knowledge", summary="绑定知识库")
def add_robot_knowledge(
    request: RobotAddKnowledgeRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    为机器人绑定知识库接口（用户权限，替换模式）
    
    - 只能绑定自己的机器人
    - 只能绑定公共知识库或自己的知识库
    - 替换模式：会先清除所有现有绑定，然后绑定新的知识库列表
    
    参数：
    - **robot_uid**: 机器人UID
    - **knowledge_uids**: 知识库UID列表
    """
    logger.info(f"用户 {current_user.uid} 为机器人 {request.robot_uid} 绑定知识库（替换模式）")
    return add_robot_knowledge_service(db, request, current_user.uid)

@router.post("/add/filter", response_model=RobotFilterOut, summary="添加过滤规则")
def add_robot_filter(
    filter_data: RobotFilterCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    为机器人添加过滤规则接口（用户权限）
    
    - 只能为自己的机器人添加过滤规则
    - 每个机器人只能有一个过滤规则
    
    参数：
    - **robot_uid**: 机器人UID
    - **filter_type**: 过滤类型（0-黑名单 1-白名单 2-混合模式）
    - **is_filter_groups**: 是否过滤群聊（可选）
    - **is_filter_private**: 是否过滤私聊（可选）
    - **is_filter_members**: 是否过滤群成员（可选）
    - **whitelist_content**: 白名单内容（可选）
    - **blacklist_content**: 黑名单内容（可选）
    - **whitelist_names**: 白名单名称（可选）
    - **blacklist_names**: 黑名单名称（可选）
    """
    logger.info(f"用户 {current_user.uid} 为机器人 {filter_data.robot_uid} 添加过滤规则")
    return add_robot_filter_service(db, filter_data, current_user.uid)