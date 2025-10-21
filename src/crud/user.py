from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from db.user import User
from typing import List, Optional
from passlib.context import CryptContext
from datetime import datetime
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

def create_user(db: Session, username: str, email: str, password: str, phone: Optional[str] = None) -> User:
    """创建用户"""
    # 检查邮箱是否已存在
    existing_user_by_email = get_user_by_email(db, email)
    if existing_user_by_email:
        raise ValueError("邮箱已被注册")
    
    # 检查用户名是否已存在
    existing_user_by_username = get_user_by_username(db, username)
    if existing_user_by_username:
        raise ValueError("用户名已被使用")
    
    hashed_password = get_password_hash(password)
    user_uid = str(uuid.uuid4())
    
    db_user = User(
        uid=user_uid,
        username=username,
        email=email,
        password_hash=hashed_password,
        phone=phone
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"User created: {db_user.username} ({db_user.email})")
    return db_user

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    return db.query(User).filter(and_(User.email == email, User.is_del == 0)).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(and_(User.username == username, User.is_del == 0)).first()

def get_user_by_uid(db: Session, uid: str) -> Optional[User]:
    """根据UID获取用户"""
    return db.query(User).filter(and_(User.uid == uid, User.is_del == 0)).first()

def get_users(db: Session, skip: int = 0, limit: int = 20) -> List[User]:
    """获取用户列表"""
    return db.query(User).filter(User.is_del == 0).offset(skip).limit(limit).all()

def get_users_count(db: Session) -> int:
    """获取用户总数"""
    return db.query(User).filter(User.is_del == 0).count()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """用户认证"""
    user = get_user_by_email(db, email)
    if not user:
        logger.warning(f"User authentication failed: email {email} not found")
        return None
    
    if not verify_password(password, user.password_hash):
        logger.warning(f"User authentication failed: incorrect password for {email}")
        return None
    
    logger.info(f"User authenticated successfully: {user.username} ({user.email})")
    return user

def update_user_last_login(db: Session, user_uid: str) -> bool:
    """更新用户最后登录时间"""
    try:
        user = get_user_by_uid(db, user_uid)
        if user:
            user.last_login_time = datetime.now()
            db.commit()
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to update last login time for user {user_uid}: {e}")
        db.rollback()
        return False

def update_user(db: Session, user_uid: str, username: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None) -> Optional[User]:
    """更新用户信息"""
    try:
        user = get_user_by_uid(db, user_uid)
        if not user:
            return None
        
        # 检查用户名是否已被其他用户使用
        if username and username != user.username:
            existing_user = get_user_by_username(db, username)
            if existing_user and existing_user.uid != user_uid:
                raise ValueError("用户名已被使用")
            user.username = username
        
        # 检查邮箱是否已被其他用户使用
        if email and email != user.email:
            existing_user = get_user_by_email(db, email)
            if existing_user and existing_user.uid != user_uid:
                raise ValueError("邮箱已被注册")
            user.email = email
        
        if phone is not None:
            user.phone = phone
        
        user.updated_time = datetime.now()
        db.commit()
        db.refresh(user)
        
        logger.info(f"User updated: {user.username} ({user.email})")
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
        
        logger.info(f"User deleted: {user.username} ({user.email})")
        return True
    except Exception as e:
        logger.error(f"Failed to delete user {user_uid}: {e}")
        db.rollback()
        return False

def search_users(db: Session, username: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None, skip: int = 0, limit: int = 20) -> tuple[List[User], int]:
    """搜索用户"""
    query = db.query(User).filter(User.is_del == 0)
    
    if username:
        query = query.filter(User.username.contains(username))
    if email:
        query = query.filter(User.email.contains(email))
    if phone:
        query = query.filter(User.phone.contains(phone))
    if start_time:
        query = query.filter(User.created_time >= start_time)
    if end_time:
        query = query.filter(User.created_time <= end_time)
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return users, total


def update_user_point(db: Session, user_uid: str, point_change: int, allow_negative: bool = False) -> Optional[User]:
    """调整用户积分
    Args:
        user_uid: 用户UID
        point_change: 积分变化量（正数增加、负数扣减）
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
        current_point = user.point or 0
        new_point = current_point + point_change
        if not allow_negative and new_point < 0:
            raise ValueError("积分不足")
        user.point = new_point
        user.updated_time = datetime.now()
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        logger.error(f"Failed to update points for user {user_uid}: {e}")
        db.rollback()
        raise