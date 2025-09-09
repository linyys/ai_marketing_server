from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from db.admin import Admin, AdminRole
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

def get_admin_by_id(db: Session, admin_id: int) -> Optional[Admin]:
    """根据ID获取管理员"""
    return db.query(Admin).filter(
        and_(Admin.id == admin_id, Admin.is_del == 0)
    ).first()

def get_admin_by_email(db: Session, email: str) -> Optional[Admin]:
    """根据邮箱获取管理员"""
    return db.query(Admin).filter(
        and_(Admin.email == email, Admin.is_del == 0)
    ).first()

def get_admin_by_username(db: Session, username: str) -> Optional[Admin]:
    """根据用户名获取管理员"""
    return db.query(Admin).filter(
        and_(Admin.username == username, Admin.is_del == 0)
    ).first()

def get_admin_by_uid(db: Session, uid: str) -> Optional[Admin]:
    """根据UID获取管理员"""
    return db.query(Admin).filter(
        and_(Admin.uid == uid, Admin.is_del == 0)
    ).first()

def get_admins(db: Session, skip: int = 0, limit: int = 20) -> List[Admin]:
    """获取管理员列表"""
    return db.query(Admin).filter(
        Admin.is_del == 0
    ).offset(skip).limit(limit).all()

def get_admins_count(db: Session) -> int:
    """获取管理员总数"""
    return db.query(Admin).filter(Admin.is_del == 0).count()

def authenticate_admin(db: Session, email: str, password: str) -> Optional[Admin]:
    """管理员认证"""
    admin = get_admin_by_email(db, email)
    if not admin:
        return None
    
    if not verify_password(password, admin.password_hash):
        return None
    
    # 更新最后登录时间
    admin.last_login_time = datetime.now()
    db.commit()
    
    logger.info(f"Admin authenticated: {admin.username} ({admin.email})")
    return admin

def update_admin_last_login(db: Session, admin_id: int) -> bool:
    """更新管理员最后登录时间"""
    admin = get_admin_by_id(db, admin_id)
    if not admin:
        return False
    
    admin.last_login_time = datetime.now()
    db.commit()
    return True

def get_admins_by_role(db: Session, role: AdminRole, skip: int = 0, limit: int = 20) -> List[Admin]:
    """根据角色获取管理员列表"""
    return db.query(Admin).filter(
        and_(Admin.role == role, Admin.is_del == 0)
    ).offset(skip).limit(limit).all()