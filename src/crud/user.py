from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from db.user import User
from schemas.user import UserCreate, UserUpdate, UserSearchParams
from typing import List, Optional
from passlib.context import CryptContext
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(
        and_(User.id == user_id, User.is_del == 0)
    ).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    return db.query(User).filter(
        and_(User.email == email, User.is_del == 0)
    ).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(
        and_(User.username == username, User.is_del == 0)
    ).first()

def get_user_by_uid(db: Session, uid: str) -> Optional[User]:
    """根据UID获取用户"""
    return db.query(User).filter(
        and_(User.uid == uid, User.is_del == 0)
    ).first()

def get_users(db: Session, skip: int = 0, limit: int = 20) -> List[User]:
    """获取用户列表"""
    return db.query(User).filter(
        User.is_del == 0
    ).offset(skip).limit(limit).all()

def get_users_count(db: Session) -> int:
    """获取用户总数"""
    return db.query(User).filter(User.is_del == 0).count()

def create_user(db: Session, user: UserCreate) -> User:
    """创建用户"""
    # 检查邮箱是否已存在
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("邮箱已存在")
    
    # 检查用户名是否已存在
    existing_username = get_user_by_username(db, user.username)
    if existing_username:
        raise ValueError("用户名已存在")
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        phone=user.phone,

        is_del=0
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"Created user: {db_user.username} ({db_user.email})")
    return db_user

def update_user(db: Session, user_id: int, update_data: UserUpdate) -> Optional[User]:
    """更新用户信息"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    update_dict = update_data.dict(exclude_unset=True)
    
    # 检查邮箱唯一性
    if 'email' in update_dict:
        existing_user = db.query(User).filter(
            and_(User.email == update_dict['email'], User.id != user_id, User.is_del == 0)
        ).first()
        if existing_user:
            raise ValueError("邮箱已存在")
    
    # 检查用户名唯一性
    if 'username' in update_dict:
        existing_user = db.query(User).filter(
            and_(User.username == update_dict['username'], User.id != user_id, User.is_del == 0)
        ).first()
        if existing_user:
            raise ValueError("用户名已存在")
    
    # 更新字段
    for field, value in update_dict.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    logger.info(f"Updated user: {user.username} ({user.email})")
    return user

def update_user_password(db: Session, user_id: int, old_password: str, new_password: str) -> bool:
    """更新用户密码"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    # 验证旧密码
    if not verify_password(old_password, user.password_hash):
        raise ValueError("原密码不正确")
    
    # 更新密码
    user.password_hash = get_password_hash(new_password)
    db.commit()
    logger.info(f"Updated password for user: {user.username}")
    return True

def soft_delete_user(db: Session, user_id: int) -> bool:
    """软删除用户"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.is_del = 1
    db.commit()
    logger.info(f"Soft deleted user: {user.username} ({user.email})")
    return True

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """用户认证"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    # 更新最后登录时间
    user.last_login_time = datetime.now()
    db.commit()
    
    logger.info(f"User authenticated: {user.username} ({user.email})")
    return user

def search_users(db: Session, search_params: UserSearchParams, skip: int = 0, limit: int = 20) -> tuple[List[User], int]:
    """搜索用户"""
    query = db.query(User).filter(User.is_del == 0)
    
    # 构建搜索条件
    conditions = []
    
    if search_params.username:
        conditions.append(User.username.like(f"%{search_params.username}%"))
    
    if search_params.email:
        conditions.append(User.email.like(f"%{search_params.email}%"))
    
    if search_params.role:
        conditions.append(User.role == search_params.role)
    
    if search_params.start_time:
        conditions.append(User.created_time >= search_params.start_time)
    
    if search_params.end_time:
        conditions.append(User.created_time <= search_params.end_time)
    
    if conditions:
        query = query.filter(and_(*conditions))
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    users = query.offset(skip).limit(limit).all()
    
    return users, total
