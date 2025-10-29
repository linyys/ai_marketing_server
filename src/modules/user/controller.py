from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from crud.user import (
    create_user,
    get_user_by_uid,
    get_users,
    get_users_count,
    update_user,
    delete_user,
    search_users,
    authenticate_user,
    update_user_password,
    verify_password,
    get_user_by_phone,
)
from schemas.user import (
    UserCreate,
    UserUpdate,
    UserOut,
    UserLogin,
    UserUpdatePassword,
    UserListResponse,
    UserSearchParams,
    Token,
    PaginationParams,
)
from utils.jwt_utils import create_access_token
from datetime import timedelta
from utils.http_request import create_post
from schemas.user import (
    ExternalSendSmsRequest,
    ExternalSendSmsResponse,
    ExternalLoginRequest,
    ExternalLoginResponse,
    ExternalSetPasswordRequest,
    ExternalBaseResponse,
    ExternalCheckTokenRequest,
    ExternalCheckTokenResponse,
)
from typing import List
import logging
import re
import uuid

logger = logging.getLogger(__name__)


def register_user_service(db: Session, user_data: UserCreate) -> UserOut:
    """用户注册服务"""
    try:
        user = create_user(
            db=db,
            username=user_data.username,
            password=user_data.password,
            phone=user_data.phone,
        )
        return UserOut.model_validate(user)
    except ValueError as e:
        logger.warning(f"用户注册失败 - 数据验证错误: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"用户注册失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户注册失败，请稍后重试",
        )


def login_user_service(db: Session, login_data: UserLogin) -> Token:
    """用户登录服务"""
    try:
        user = authenticate_user(db, login_data.phone, login_data.password)
        if not user:
            logger.warning(f"用户登录失败: 手机号或密码错误 - {login_data.phone}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="手机号或密码错误"
            )

        # 生成访问令牌
        access_token = create_access_token(
            data={
                "sub": user.uid,
                "phone": user.phone,
                "role": "user",
                "is_admin": False,
            }
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600,
            user_info=UserOut.model_validate(user),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试",
        )


def get_user_service(db: Session, uid: str) -> UserOut:
    """获取用户服务"""
    try:
        user = get_user_by_uid(db, uid)
        if not user:
            logger.warning(f"用户不存在: UID={uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
            )
        return UserOut.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败，请稍后重试",
        )


def get_users_list_service(
    db: Session, skip: int = 0, limit: int = 20
) -> UserListResponse:
    """获取用户列表服务"""
    try:
        users = get_users(db, skip=skip, limit=limit)
        total = get_users_count(db)

        return UserListResponse(
            total=total,
            items=[UserOut.model_validate(user) for user in users],
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        logger.error(f"获取用户列表失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表失败，请稍后重试",
        )


def update_user_service(db: Session, uid: str, user_data: UserUpdate) -> UserOut:
    """更新用户服务"""
    try:
        user = update_user(
            db=db,
            user_uid=uid,
            username=user_data.username,
            phone=user_data.phone,
        )
        if not user:
            logger.warning(f"用户不存在: UID={uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
            )
        return UserOut.model_validate(user)
    except ValueError as e:
        logger.warning(f"更新用户失败 - 数据验证错误: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户失败，请稍后重试",
        )


def delete_user_service(db: Session, uid: str) -> dict:
    """删除用户服务"""
    try:
        success = delete_user(db, uid)
        if not success:
            logger.warning(f"用户不存在: UID={uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
            )

        logger.info(f"用户删除成功: UID={uid}")
        return {"message": "用户删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除用户失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户失败，请稍后重试",
        )


def search_users_service(
    db: Session, search_params: UserSearchParams, skip: int = 0, limit: int = 20
) -> UserListResponse:
    """搜索用户服务"""
    try:
        users, total = search_users(
            db=db,
            username=search_params.username,
            phone=search_params.phone,
            start_time=search_params.start_time,
            end_time=search_params.end_time,
            skip=skip,
            limit=limit,
        )

        return UserListResponse(
            total=total,
            items=[UserOut.model_validate(user) for user in users],
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        logger.error(f"搜索用户失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="搜索用户失败，请稍后重试",
        )


def update_password_service(
    db: Session, uid: str, password_data: UserUpdatePassword, current_user_uid: str
) -> dict:
    """修改密码服务"""
    try:
        # 获取用户信息
        user = get_user_by_uid(db, uid)
        if not user:
            logger.warning(f"用户不存在: UID={uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
            )

        # 验证旧密码（只有本人修改时需要验证）
        if uid == current_user_uid:
            if not verify_password(password_data.old_password, user.password_hash):
                logger.warning(f"修改密码失败: 原密码错误 - UID={uid}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误"
                )

        # 更新密码
        success = update_user_password(db, uid, password_data.new_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="密码更新失败"
            )

        logger.info(f"密码修改成功: UID={uid}")
        return {"message": "密码修改成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码失败 - 系统错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败，请稍后重试",
        )


# ==========================
# 外部认证相关服务函数（百科学）
# ==========================

BAIKEXUE_BASE_URL = "https://www.baikexue.cn"
DEFAULT_HEADERS = {"Content-Type": "application/json"}


async def external_send_sms_code_service(
    req: ExternalSendSmsRequest,
) -> ExternalSendSmsResponse:
    """调用外部接口发送验证码"""
    post = create_post(BAIKEXUE_BASE_URL, DEFAULT_HEADERS)
    # 外部接口参数名已更正为 phone
    payload = {"phone": req.phone}
    res = await post("/api/agent/send_sms_code.php", json=payload)
    # 仅按文档字段解析（code/txt）
    try:
        code_val = res.get("code") if isinstance(res, dict) else None
        try:
            code_int = int(code_val) if code_val is not None else 400
        except Exception:
            code_int = 400
        txt_val = res.get("txt") if isinstance(res, dict) else None
        return ExternalSendSmsResponse(code=code_int, txt=txt_val)
    except Exception:
        # 回退：尽量返回结构化的错误
        return ExternalSendSmsResponse(code=400, txt="发送验证码失败")


async def external_login_service(
    db: Session, req: ExternalLoginRequest
) -> ExternalLoginResponse:
    """调用外部接口进行登录（验证码登录或密码登录）"""
    # 参数校验：根据 state 判断必填字段
    if req.state == 1 and not req.code:
        # 直接返回外部风格的错误码，不抛 HTTP 异常
        return ExternalLoginResponse(code=400, txt="验证码缺失", data=None)
    if req.state == 2 and not req.password:
        return ExternalLoginResponse(code=400, txt="密码缺失", data=None)

    post = create_post(BAIKEXUE_BASE_URL, DEFAULT_HEADERS)
    payload = {
        "action": "login",
        "state": req.state,
        "phone": req.phone,
    }
    if req.state == 1:
        payload["code"] = req.code
    else:
        payload["password"] = req.password

    res = await post("/api/agent/user.php", json=payload)
    logger.debug(f"外部登录原始响应: {res}")
    # 构造响应并尽量附带本地短期JWT
    try:
        # 仅按文档字段解析
        code_val = res.get("code") if isinstance(res, dict) else None
        try:
            code_int = int(code_val) if code_val is not None else None
        except Exception:
            code_int = None

        txt_val = res.get("txt") if isinstance(res, dict) else None

        raw_data = res.get("data") if isinstance(res, dict) else None

        safe_data = None
        if isinstance(raw_data, dict):
            data = dict(raw_data)  # 浅拷贝避免修改原对象
            # 标准化 id 为字符串
            if "id" in data and not isinstance(data.get("id"), str):
                try:
                    data["id"] = str(data.get("id"))
                except Exception:
                    data["id"] = None
            # 标准化 phone
            if "phone" in data and data.get("phone") is not None:
                phone_norm = str(data.get("phone")).strip()
            else:
                phone_norm = str(req.phone or "").strip()
            phone_norm = re.sub(r"[\s\-\(\)]", "", phone_norm)
            if phone_norm.startswith("+86"):
                phone_norm = phone_norm[3:]
            data["phone"] = phone_norm

            # token 统一转字符串（若存在）
            if "token" in data and data.get("token") is not None and not isinstance(data.get("token"), str):
                try:
                    data["token"] = str(data.get("token"))
                except Exception:
                    pass

            # 仅当关键字段齐全时才返回 data，避免模型解析失败
            if data.get("id") and data.get("phone") and data.get("token"):
                safe_data = data

        # 若外部登录成功，尝试按手机号绑定本地用户并签发本地短期JWT（3小时）
        if (code_int == 200 or (isinstance(res, dict) and res.get("code") == 200)) and isinstance(safe_data, dict):
            # 优先外部返回手机号，缺失时回退到请求手机号
            raw_phone = safe_data.get("phone") or req.phone
            phone = str(raw_phone or "").strip()
            # 轻量规范化：去除常见分隔符与国家码+86（如存在）
            phone = re.sub(r"[\s\-\(\)]", "", phone)
            if phone.startswith("+86"):
                phone = phone[3:]
            if phone:
                user = get_user_by_phone(db, phone)
                if not user:
                    nickname = safe_data.get("nickname") or "user"
                    # 清理用户名，保留常见安全字符
                    base_username = re.sub(r"[^\w\-\.\s]", "_", str(nickname).strip()) or "user"
                    if len(base_username) < 3:
                        base_username = (base_username + "_user")[:3]
                    # 使用手机号作为后缀保证唯一性
                    generated_username = f"{base_username}"
                    random_password = uuid.uuid4().hex
                    avatar_url = str(safe_data.get("avatar") or "").strip()
                    try:
                        user = create_user(
                            db=db,
                            username=generated_username,
                            password=random_password,
                            phone=phone,
                            avatar=avatar_url,
                        )
                    except ValueError:
                        # 退化为固定前缀方案避免冲突
                        fallback_username = f"user_{phone}"
                        user = create_user(
                            db=db,
                            username=fallback_username,
                            password=random_password,
                            phone=phone,
                            avatar=avatar_url,
                        )
                else:
                    # 已存在用户：若外部返回头像且非空，更新本地头像
                    ext_avatar = str((safe_data or {}).get("avatar") or "").strip()
                    if ext_avatar:
                        update_user(db=db, user_uid=user.uid, avatar=ext_avatar)
                if user:
                    ttl_minutes = 180
                    access_token = create_access_token(
                        data={
                            "sub": user.uid,
                            "phone": user.phone,
                            "role": "user",
                            "is_admin": False,
                            "provider": "external",
                        },
                        expires_delta=timedelta(minutes=ttl_minutes),
                    )
                    local_access_token = access_token
                    local_expires_in = ttl_minutes * 60
                else:
                    local_access_token = None
                    local_expires_in = None
            else:
                local_access_token = None
                local_expires_in = None
        else:
            local_access_token = None
            local_expires_in = None

        # 构建最终响应，避免传递未知字段导致模型校验失败
        final_resp = {
            "code": code_int if code_int is not None else (res.get("code") if isinstance(res, dict) else 400),
            "txt": txt_val,
            "data": safe_data,
            "local_access_token": local_access_token,
            "local_expires_in": local_expires_in,
        }
        return ExternalLoginResponse(**final_resp)
    except Exception as e:
        logger.error(f"外部登录响应解析异常: {e}")
        # 兜底：尽量返回外部 code 与文案
        code_fallback = res.get("code", 400) if isinstance(res, dict) else 400
        txt_fallback = res.get("txt") if isinstance(res, dict) else None
        return ExternalLoginResponse(code=code_fallback, txt=txt_fallback, data=None)


async def external_set_password_service(
    req: ExternalSetPasswordRequest,
) -> ExternalBaseResponse:
    """调用外部接口初次设置密码"""
    post = create_post(BAIKEXUE_BASE_URL, DEFAULT_HEADERS)
    payload = {
        "action": "setPassword",
        "token": req.token,
        "password": req.password,
        "password2": req.password2,
    }
    res = await post("/api/agent/user.php", json=payload)
    return ExternalBaseResponse(**res)


async def external_check_token_service(
    db: Session, req: ExternalCheckTokenRequest
) -> ExternalCheckTokenResponse:
    """调用外部接口检查登录状态"""
    post = create_post(BAIKEXUE_BASE_URL, DEFAULT_HEADERS)
    payload = {
        "action": "checkToken",
        "token": req.token,
    }
    res = await post("/api/agent/user.php", json=payload)
    logger.debug(f"外部检查token原始响应: {res}")
    try:
        # 仅按文档字段解析
        code_val = res.get("code") if isinstance(res, dict) else None
        try:
            code_int = int(code_val) if code_val is not None else None
        except Exception:
            code_int = None

        txt_val = res.get("txt") if isinstance(res, dict) else None

        raw_data = res.get("data") if isinstance(res, dict) else None

        safe_data = None
        if isinstance(raw_data, dict):
            data = dict(raw_data)
            if "id" in data and not isinstance(data.get("id"), str):
                try:
                    data["id"] = str(data.get("id"))
                except Exception:
                    data["id"] = None
            # 若外部token有效，尝试生成本地短期JWT（3小时）
            if (code_int == 200 or (isinstance(res, dict) and res.get("code") == 200)):
                raw_phone = data.get("phone")
                phone = str(raw_phone or "").strip()
                phone = re.sub(r"[\s\-\(\)]", "", phone)
                if phone.startswith("+86"):
                    phone = phone[3:]
                if phone:
                    user = get_user_by_phone(db, phone)
                    if not user:
                        nickname = data.get("nickname") or "user"
                        base_username = re.sub(r"[^\w\-\.\s]", "_", str(nickname).strip()) or "user"
                        if len(base_username) < 3:
                            base_username = (base_username + "_user")[:3]
                        generated_username = f"{base_username}_{phone}"
                        random_password = uuid.uuid4().hex
                        avatar_url = str(data.get("avatar") or "").strip()
                        try:
                            user = create_user(
                                db=db,
                                username=generated_username,
                                password=random_password,
                                phone=phone,
                                avatar=avatar_url,
                            )
                        except ValueError:
                            fallback_username = f"user_{phone}"
                            user = create_user(
                                db=db,
                                username=fallback_username,
                                password=random_password,
                                phone=phone,
                                avatar=avatar_url,
                            )
                    else:
                        # 已存在用户：若外部返回头像且非空，更新本地头像
                        ext_avatar = str((data or {}).get("avatar") or "").strip()
                        if ext_avatar:
                            update_user(db=db, user_uid=user.uid, avatar=ext_avatar)
                    if user:
                        ttl_minutes = 180
                        access_token = create_access_token(
                            data={
                                "sub": user.uid,
                                "phone": user.phone,
                                "role": "user",
                                "is_admin": False,
                                "provider": "external",
                            },
                            expires_delta=timedelta(minutes=ttl_minutes),
                        )
                        local_access_token = access_token
                        local_expires_in = ttl_minutes * 60
                    else:
                        local_access_token = None
                        local_expires_in = None
                else:
                    local_access_token = None
                    local_expires_in = None
            else:
                local_access_token = None
                local_expires_in = None
            # data 必须具备必要字段时才返回
            if data.get("id") and data.get("phone") and data.get("token"):
                safe_data = data

        final_resp = {
            "code": code_int if code_int is not None else (res.get("code") if isinstance(res, dict) else 400),
            "txt": txt_val,
            "data": safe_data,
            "local_access_token": locals().get("local_access_token"),
            "local_expires_in": locals().get("local_expires_in"),
        }
        # 返回时附带可选的本地JWT字段
        return ExternalCheckTokenResponse(**final_resp)
    except Exception as e:
        logger.error(f"外部检查token响应解析异常: {e}")
        code_fallback = res.get("code", 400) if isinstance(res, dict) else 400
        txt_fallback = res.get("txt") if isinstance(res, dict) else None
        return ExternalCheckTokenResponse(code=code_fallback, txt=txt_fallback, data=None)
