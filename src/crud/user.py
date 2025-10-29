from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, text
from db.user import User
from typing import List, Optional
from passlib.context import CryptContext
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import logging
import uuid

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

def create_user(db: Session, username: str, password: str, phone: Optional[str] = None, avatar: Optional[str] = "") -> User:
    """创建用户
    - 允许重复用户名
    - 移除邮箱相关逻辑
    - 若提供手机号，依赖数据库唯一约束确保一号一用户
    """
    hashed_password = get_password_hash(password)
    user_uid = str(uuid.uuid4())

    db_user = User(
        uid=user_uid,
        username=username,
        password_hash=hashed_password,
        phone=phone,
        avatar=(avatar or "")
    )

    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        logger.info(f"User created: {db_user.username} (phone={db_user.phone})")
        return db_user
    except IntegrityError as e:
        # 处理手机号唯一约束冲突：若存在被软删除的同号用户，则复活之
        db.rollback()
        if phone:
            existing = db.query(User).filter(User.phone == phone).first()
            if existing:
                if getattr(existing, "is_del", 0) == 1:
                    # 复活软删除用户，并更新必要字段
                    existing.is_del = 0
                    existing.username = username or existing.username
                    existing.password_hash = hashed_password
                    if avatar is not None:
                        existing.avatar = avatar or ""
                    existing.updated_time = datetime.now()
                    db.commit()
                    db.refresh(existing)
                    logger.info(
                        f"Revived soft-deleted user for phone={phone}, username={existing.username}"
                    )
                    return existing
                else:
                    # 已存在未删除同号用户
                    logger.warning(
                        f"Attempt to create user with existing phone (not deleted): {phone}"
                    )
                    raise ValueError("手机号已存在")
        # 其他唯一性冲突或未知错误
        logger.error(f"IntegrityError when creating user: {e}")
        raise

# 移除邮箱检索：邮箱字段已删除

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(and_(User.username == username, User.is_del == 0)).first()

def get_user_by_uid(db: Session, uid: str) -> Optional[User]:
    """根据UID获取用户"""
    return db.query(User).filter(and_(User.uid == uid, User.is_del == 0)).first()

def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    """根据手机号获取用户"""
    return db.query(User).filter(and_(User.phone == phone, User.is_del == 0)).first()

def get_users(db: Session, skip: int = 0, limit: int = 20) -> List[User]:
    """获取用户列表"""
    return db.query(User).filter(User.is_del == 0).offset(skip).limit(limit).all()

def get_users_count(db: Session) -> int:
    """获取用户总数"""
    return db.query(User).filter(User.is_del == 0).count()

def authenticate_user(db: Session, phone: str, password: str) -> Optional[User]:
    """用户认证（基于手机号）"""
    user = get_user_by_phone(db, phone)
    if not user:
        logger.warning(f"User authentication failed: phone {phone} not found")
        return None

    if not verify_password(password, user.password_hash):
        logger.warning(f"User authentication failed: incorrect password for phone {phone}")
        return None

    logger.info(f"User authenticated successfully: {user.username} (phone={user.phone})")
    return user

# 移除最后登录时间逻辑：不再维护 users.last_login_time 字段

def update_user(db: Session, user_uid: str, username: Optional[str] = None, phone: Optional[str] = None, avatar: Optional[str] = None) -> Optional[User]:
    """更新用户信息（移除邮箱逻辑，用户名允许重复）"""
    try:
        user = get_user_by_uid(db, user_uid)
        if not user:
            return None
        
        # 用户名允许重复，直接更新
        if username is not None:
            user.username = username

        if phone is not None:
            user.phone = phone
        
        if avatar is not None:
            user.avatar = avatar or ""
        
        user.updated_time = datetime.now()
        db.commit()
        db.refresh(user)
        
        logger.info(f"User updated: {user.username} (phone={user.phone})")
        return user
    except Exception as e:
        logger.error(f"Failed to update user {user_uid}: {e}")
        db.rollback()
        raise

def update_user_password(db: Session, user_uid: str, new_password: str) -> bool:
    """更新用户密码"""
    try:
        user = get_user_by_uid(db, user_uid)
        if not user:
            return False
        
        user.password_hash = get_password_hash(new_password)
        user.updated_time = datetime.now()
        db.commit()
        
        logger.info(f"Password updated for user: {user.username}")
        return True
    except Exception as e:
        logger.error(f"Failed to update password for user {user_uid}: {e}")
        db.rollback()
        return False

def delete_user(db: Session, user_uid: str) -> bool:
    """软删除用户"""
    try:
        user = get_user_by_uid(db, user_uid)
        if not user:
            return False
        
        user.is_del = 1
        user.updated_time = datetime.now()
        db.commit()
        
        logger.info(f"User deleted: {user.username} (phone={user.phone})")
        return True
    except Exception as e:
        logger.error(f"Failed to delete user {user_uid}: {e}")
        db.rollback()
        return False

def search_users(db: Session, username: Optional[str] = None, phone: Optional[str] = None, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None, skip: int = 0, limit: int = 20) -> tuple[List[User], int]:
    """搜索用户（移除邮箱字段）"""
    query = db.query(User).filter(User.is_del == 0)
    
    if username:
        query = query.filter(User.username.contains(username))
    if phone:
        query = query.filter(User.phone.contains(phone))
    if start_time:
        query = query.filter(User.created_time >= start_time)
    if end_time:
        query = query.filter(User.created_time <= end_time)
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return users, total


def update_user_point(db: Session, user_uid: str, point_change: Decimal, allow_negative: bool = False) -> Optional[User]:
    """调整用户积分
    Args:
        user_uid: 用户UID
        point_change: 积分变化量（Decimal，正数增加、负数扣减）
        allow_negative: 是否允许结果为负数（流式场景可为True）
    Returns:
        更新后的User或None
    Raises:
        ValueError: 当积分不足且不允许负数时抛出
    """
    try:
        user = get_user_by_uid(db, user_uid)
        if not user:
            return None

        # 量化积分变化到6位小数，避免浮动误差
        change = Decimal(point_change or 0).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)

        # 原子更新：在一条SQL中同时完成扣减与非负校验（当不允许负数时）
        result = db.execute(
            text(
                """
                UPDATE users
                SET point = point + :delta, updated_time = NOW()
                WHERE uid = :uid
                  AND (:allow_neg = 1 OR point + :delta >= 0)
                """
            ),
            {"delta": change, "uid": user_uid, "allow_neg": 1 if allow_negative else 0},
        )

        if result.rowcount == 0:
            # 要么用户不存在（已在前面判断），要么积分不足且不允许负数
            raise ValueError("积分不足")

        db.commit()

        # 重新读取最新积分值
        updated = get_user_by_uid(db, user_uid)
        return updated
    except Exception as e:
        logger.error(f"Failed to update points for user {user_uid}: {e}")
        db.rollback()
        raise