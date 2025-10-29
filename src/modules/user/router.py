from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.user import (
    UserCreate,
    UserUpdate,
    UserOut,
    UserLogin,
    UserUpdatePassword,
    UserListResponse,
    UserSearchParams,
    Token,
    ExternalSendSmsRequest,
    ExternalSendSmsResponse,
    ExternalLoginRequest,
    ExternalLoginResponse,
    ExternalSetPasswordRequest,
    ExternalBaseResponse,
    ExternalCheckTokenRequest,
    ExternalCheckTokenResponse,
)
from modules.user.controller import (
    register_user_service,
    login_user_service,
    get_user_service,
    get_users_list_service,
    update_user_service,
    delete_user_service,
    search_users_service,
    update_password_service,
    external_send_sms_code_service,
    external_login_service,
    external_set_password_service,
    external_check_token_service,
)
from utils.auth import get_current_admin_or_user, get_current_user, get_current_admin
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["用户"], prefix="/user")


@router.post("/login", response_model=Token, summary="用户登录")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录接口"""
    logger.info(f"用户登录请求: {login_data.phone}")
    return login_user_service(db, login_data)


@router.get("/list", response_model=UserListResponse, summary="获取用户列表")
def get_users_list(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """获取用户列表接口（仅管理员可访问）"""
    logger.info(f"管理员 {current_admin.username} 请求用户列表")
    return get_users_list_service(db, skip, limit)


@router.get("/get/me", response_model=UserOut, summary="获取当前用户信息")
def get_current_user_info(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """获取当前用户信息接口（根据token获取）"""
    logger.info(f"用户 {current_user.uid} 请求自己的信息")
    return get_user_service(db, current_user.uid)


@router.get("/get/{uid}", response_model=UserOut, summary="获取指定用户信息")
def get_user(
    uid: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_or_user),
):
    """获取指定用户信息接口（管理员或本人可访问）"""
    # 检查权限：管理员或本人
    from db.admin import Admin

    is_admin = isinstance(current_user, Admin)

    if is_admin:
        logger.info(f"管理员 {current_user.username} 请求用户信息: {uid}")
    else:
        # 非管理员，检查是否为本人
        if uid != current_user.uid:
            logger.warning(f"用户 {current_user.uid} 尝试访问其他用户信息: {uid}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问其他用户信息"
            )
        logger.info(f"用户 {current_user.uid} 请求自己的信息")

    return get_user_service(db, uid)


@router.post("/search", response_model=UserListResponse, summary="搜索用户")
def search_users(
    search_params: UserSearchParams,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数限制"),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """搜索用户接口（仅管理员可访问）"""
    logger.info(f"管理员 {current_admin.username} 搜索用户")
    return search_users_service(db, search_params, skip, limit)


@router.post("/update/password", summary="修改密码")
def update_password(
    uid: str,
    password_data: UserUpdatePassword,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """修改密码接口（管理员或本人可访问）"""
    # 检查权限：管理员或本人
    try:
        # 尝试获取管理员权限
        from utils.auth import get_external_current_admin

        admin = get_external_current_admin()
        logger.info(f"管理员 {admin.username} 修改用户密码: {uid}")
    except:
        # 非管理员，检查是否为本人
        if uid != current_user.uid:
            logger.warning(f"用户 {current_user.uid} 尝试修改其他用户密码: {uid}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权限修改其他用户密码"
            )
        logger.info(f"用户 {current_user.uid} 修改自己的密码")

    return update_password_service(db, uid, password_data, current_user.uid)


# ==========================
# 外部认证相关路由（百可学）
# ==========================


@router.post(
    "/external/send_sms_code",
    response_model=ExternalSendSmsResponse,
    summary="外部接口-发送验证码",
)
async def external_send_sms_code(
    req: ExternalSendSmsRequest,
):
    logger.info(f"外部接口发送验证码: {req.phone}")
    return await external_send_sms_code_service(req)


@router.post(
    "/external/login", response_model=ExternalLoginResponse, summary="外部接口-登录"
)
async def external_login(
    req: ExternalLoginRequest,
    db: Session = Depends(get_db),
):
    logger.info(f"外部接口登录: state={req.state}, phone={req.phone}")
    return await external_login_service(db, req)


@router.post(
    "/external/set_password",
    response_model=ExternalBaseResponse,
    summary="外部接口-初次设置密码",
)
async def external_set_password(
    req: ExternalSetPasswordRequest,
):
    logger.info("外部接口初次设置密码")
    return await external_set_password_service(req)

@router.post(
    "/external/check_token",
    response_model=ExternalCheckTokenResponse,
    summary="外部接口-检查登录状态",
)
async def external_check_token(
    req: ExternalCheckTokenRequest,
    db: Session = Depends(get_db),
):
    logger.info("外部接口检查登录状态")
    return await external_check_token_service(db, req)
