from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from crud.robot import (
    create_robot,
    get_robot_by_uid,
    get_robots,
    get_robots_count,
    get_robots_by_user,
    get_robots_by_user_count,
    update_robot,
    delete_robot,
    search_robots,
    search_user_robots,
    check_robot_permission,
    add_robot_knowledges,
    create_robot_filter,
    get_robot_filter_by_robot_uid,
    get_robot_knowledges
)
from crud.knowledge import get_knowledge_by_uid
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
from typing import List
import logging

logger = logging.getLogger(__name__)

def create_robot_service(db: Session, robot_data: RobotCreate, user_uid: str) -> RobotOut:
    """
    创建机器人服务
    
    Args:
        db: 数据库会话
        robot_data: 机器人创建数据
        user_uid: 用户UID
    
    Returns:
        创建的机器人信息
    
    Raises:
        HTTPException: 创建失败时抛出异常
    """
    try:
        # 验证平台和登录类型的组合
        if robot_data.platform in [0, 1] and robot_data.login_type != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="微信和企业微信只支持扫码登录"
            )
        
        if robot_data.platform in [3, 4] and robot_data.login_type != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="抖音和小红书只支持账号密码登录"
            )
        
        # 验证平台和回复类型的组合
        if robot_data.platform in [0, 1] and robot_data.reply_type not in [2, 3]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="微信和企业微信只支持群聊和私聊回复"
            )
        
        if robot_data.platform in [3, 4] and robot_data.reply_type not in [0, 1]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="抖音和小红书只支持评论和私信回复"
            )
        
        # 如果是账号密码登录，验证账号和密码是否提供
        if robot_data.login_type == 0 and (not robot_data.account or not robot_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账号密码登录需要提供账号和密码"
            )
        
        robot = create_robot(
            db=db,
            name=robot_data.name,
            reply_type=robot_data.reply_type,
            platform=robot_data.platform,
            login_type=robot_data.login_type,
            description=robot_data.description,
            from_user_uid=user_uid,
            account=robot_data.account,
            password=robot_data.password
        )
        
        logger.info(f"用户 {user_uid} 创建机器人成功: {robot.uid}")
        return RobotOut.model_validate(robot)
    
    except ValueError as e:
        logger.error(f"创建机器人失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建机器人异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建机器人失败"
        )

def get_robots_list_service(db: Session, skip: int, limit: int, is_admin: bool = False, 
                           user_uid: str = None) -> RobotListResponse:
    """
    获取机器人列表服务
    
    Args:
        db: 数据库会话
        skip: 跳过数量
        limit: 限制数量
        is_admin: 是否为管理员
        user_uid: 用户UID（非管理员时必需）
    
    Returns:
        机器人列表响应
    """
    try:
        if is_admin:
            robots = get_robots(db, skip, limit)
            total = get_robots_count(db)
            logger.info(f"管理员获取机器人列表，总数: {total}")
        else:
            if not user_uid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户UID不能为空"
                )
            robots = get_robots_by_user(db, user_uid, skip, limit)
            total = get_robots_by_user_count(db, user_uid)
            logger.info(f"用户 {user_uid} 获取机器人列表，总数: {total}")
        
        robot_outs = [RobotOut.model_validate(robot) for robot in robots]
        
        return RobotListResponse(
            total=total,
            items=robot_outs,
            skip=skip,
            limit=limit
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取机器人列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取机器人列表失败"
        )

def search_robots_service(db: Session, search_params: RobotSearchParams, skip: int, limit: int,
                         is_admin: bool = False, user_uid: str = None) -> RobotListResponse:
    """
    搜索机器人服务
    
    Args:
        db: 数据库会话
        search_params: 搜索参数
        skip: 跳过数量
        limit: 限制数量
        is_admin: 是否为管理员
        user_uid: 用户UID（非管理员时必需）
    
    Returns:
        机器人列表响应
    """
    try:
        if is_admin:
            robots, total = search_robots(
                db=db,
                name=search_params.name,
                platform=search_params.platform,
                is_enable=search_params.is_enable,
                from_user_uid=search_params.from_user_uid,
                start_time=search_params.start_time,
                end_time=search_params.end_time,
                skip=skip,
                limit=limit
            )
            logger.info(f"管理员搜索机器人，结果数: {total}")
        else:
            if not user_uid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户UID不能为空"
                )
            robots, total = search_user_robots(
                db=db,
                user_uid=user_uid,
                name=search_params.name,
                platform=search_params.platform,
                is_enable=search_params.is_enable,
                start_time=search_params.start_time,
                end_time=search_params.end_time,
                skip=skip,
                limit=limit
            )
            logger.info(f"用户 {user_uid} 搜索机器人，结果数: {total}")
        
        robot_outs = [RobotOut.model_validate(robot) for robot in robots]
        
        return RobotListResponse(
            total=total,
            items=robot_outs,
            skip=skip,
            limit=limit
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索机器人失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="搜索机器人失败"
        )

def get_robot_service(db: Session, robot_uid: str, current_user_uid: str, is_admin: bool = False) -> RobotOut:
    """
    获取单个机器人服务
    
    Args:
        db: 数据库会话
        robot_uid: 机器人UID
        current_user_uid: 当前用户UID
        is_admin: 是否为管理员
    
    Returns:
        机器人信息
    
    Raises:
        HTTPException: 获取失败时抛出异常
    """
    try:
        robot = get_robot_by_uid(db, robot_uid)
        if not robot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="机器人不存在"
            )
        
        # 权限检查：管理员或机器人所有者
        if not is_admin and robot.from_user_uid != current_user_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限访问此机器人"
            )
        
        logger.info(f"获取机器人详情成功: {robot_uid}")
        return RobotOut.model_validate(robot)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取机器人详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取机器人详情失败"
        )

def update_robot_service(db: Session, robot_uid: str, robot_data: RobotUpdate, 
                        current_user_uid: str, is_admin: bool = False) -> RobotOut:
    """
    更新机器人服务
    
    Args:
        db: 数据库会话
        robot_uid: 机器人UID
        robot_data: 更新数据
        current_user_uid: 当前用户UID
        is_admin: 是否为管理员
    
    Returns:
        更新后的机器人信息
    
    Raises:
        HTTPException: 更新失败时抛出异常
    """
    try:
        # 权限检查
        has_permission, robot = check_robot_permission(db, robot_uid, current_user_uid)
        if not robot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="机器人不存在"
            )
        
        if not is_admin and not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限修改此机器人"
            )
        
        # 验证平台和登录类型的组合（如果有更新）
        platform = robot_data.platform if robot_data.platform is not None else robot.platform
        login_type = robot_data.login_type if robot_data.login_type is not None else robot.login_type
        reply_type = robot_data.reply_type if robot_data.reply_type is not None else robot.reply_type
        
        if platform in [0, 1] and login_type != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="微信和企业微信只支持扫码登录"
            )
        
        if platform in [3, 4] and login_type != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="抖音和小红书只支持账号密码登录"
            )
        
        if platform in [0, 1] and reply_type not in [2, 3]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="微信和企业微信只支持群聊和私聊回复"
            )
        
        if platform in [3, 4] and reply_type not in [0, 1]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="抖音和小红书只支持评论和私信回复"
            )
        
        updated_robot = update_robot(
            db=db,
            robot_uid=robot_uid,
            name=robot_data.name,
            reply_type=robot_data.reply_type,
            account=robot_data.account,
            password=robot_data.password,
            platform=robot_data.platform,
            login_type=robot_data.login_type,
            description=robot_data.description,
            is_enable=robot_data.is_enable
        )
        
        if not updated_robot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="机器人不存在"
            )
        
        logger.info(f"机器人更新成功: {robot_uid}")
        return RobotOut.model_validate(updated_robot)
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"更新机器人失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"更新机器人异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新机器人失败"
        )

def delete_robot_service(db: Session, delete_request: RobotDeleteRequest, 
                        current_user_uid: str, is_admin: bool = False) -> dict:
    """
    删除机器人服务
    
    Args:
        db: 数据库会话
        delete_request: 删除请求
        current_user_uid: 当前用户UID
        is_admin: 是否为管理员
    
    Returns:
        删除结果
    
    Raises:
        HTTPException: 删除失败时抛出异常
    """
    try:
        # 权限检查
        has_permission, robot = check_robot_permission(db, delete_request.uid, current_user_uid)
        if not robot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="机器人不存在"
            )
        
        if not is_admin and not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限删除此机器人"
            )
        
        success = delete_robot(db, delete_request.uid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="机器人不存在"
            )
        
        logger.info(f"机器人删除成功: {delete_request.uid}")
        return {"message": "机器人删除成功"}
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"删除机器人失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"删除机器人异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除机器人失败"
        )

def add_robot_knowledge_service(db: Session, request: RobotAddKnowledgeRequest, 
                               current_user_uid: str) -> dict:
    """
    为机器人绑定知识库服务（替换模式）
    
    Args:
        db: 数据库会话
        request: 绑定请求
        current_user_uid: 当前用户UID
    
    Returns:
        绑定结果
    
    Raises:
        HTTPException: 绑定失败时抛出异常
    """
    try:
        # 权限检查
        has_permission, robot = check_robot_permission(db, request.robot_uid, current_user_uid)
        if not robot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="机器人不存在"
            )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限操作此机器人"
            )
        
        # 验证知识库是否存在且用户有权限访问
        for knowledge_uid in request.knowledge_uids:
            knowledge = get_knowledge_by_uid(db, knowledge_uid)
            if not knowledge:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"知识库 {knowledge_uid} 不存在"
                )
            
            # 检查知识库权限：公共知识库或用户自己的知识库
            if knowledge.from_user and knowledge.from_user != current_user_uid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"无权限访问知识库 {knowledge_uid}"
                )
        
        success = add_robot_knowledges(db, request.robot_uid, request.knowledge_uids)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="绑定知识库失败"
            )
        
        logger.info(f"机器人 {request.robot_uid} 绑定知识库成功（替换模式）")
        return {"message": "绑定知识库成功"}
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"绑定知识库失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"绑定知识库异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="绑定知识库失败"
        )

def add_robot_filter_service(db: Session, filter_data: RobotFilterCreate, 
                            current_user_uid: str) -> RobotFilterOut:
    """
    为机器人添加过滤规则服务
    
    Args:
        db: 数据库会话
        filter_data: 过滤规则数据
        current_user_uid: 当前用户UID
    
    Returns:
        创建的过滤规则信息
    
    Raises:
        HTTPException: 创建失败时抛出异常
    """
    try:
        # 权限检查
        has_permission, robot = check_robot_permission(db, filter_data.robot_uid, current_user_uid)
        if not robot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="机器人不存在"
            )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限操作此机器人"
            )
        
        # 验证过滤规则的内容要求
        if filter_data.filter_type == 0 and not filter_data.blacklist_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="黑名单模式必须提供黑名单内容"
            )
        
        if filter_data.filter_type == 1 and not filter_data.whitelist_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="白名单模式必须提供白名单内容"
            )
        
        if filter_data.filter_type == 2 and (not filter_data.whitelist_content or not filter_data.blacklist_content):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="混合模式必须同时提供白名单和黑名单内容"
            )
        
        robot_filter = create_robot_filter(
            db=db,
            robot_uid=filter_data.robot_uid,
            filter_type=filter_data.filter_type,
            is_filter_groups=filter_data.is_filter_groups,
            is_filter_private=filter_data.is_filter_private,
            is_filter_members=filter_data.is_filter_members,
            whitelist_content=filter_data.whitelist_content,
            blacklist_content=filter_data.blacklist_content,
            whitelist_names=filter_data.whitelist_names,
            blacklist_names=filter_data.blacklist_names
        )
        
        logger.info(f"机器人 {filter_data.robot_uid} 添加过滤规则成功")
        return RobotFilterOut.model_validate(robot_filter)
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"添加过滤规则失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"添加过滤规则异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加过滤规则失败"
        )