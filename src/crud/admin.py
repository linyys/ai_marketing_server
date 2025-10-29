from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from db.admin import Admin
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

def create_admin(db: Session, username: str, email: str, password: str, phone: Optional[str] = None) -> Admin:
    """创建管理员"""
    # 检查邮箱是否已存在
    existing_admin_by_email = get_admin_by_email(db, email)
    if existing_admin_by_email:
        raise ValueError("邮箱已被注册")
    
    # 检查用户名是否已存在
    existing_admin_by_username = get_admin_by_username(db, username)
    if existing_admin_by_username:
        raise ValueError("用户名已被使用")
    
    hashed_password = get_password_hash(password)
    admin_uid = str(uuid.uuid4())
    
    db_admin = Admin(
        uid=admin_uid,
        username=username,
        email=email,
        password_hash=hashed_password,
        phone=phone
    )
    
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    
    logger.info(f"Admin created: {db_admin.username} ({db_admin.email})")
    return db_admin

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

def get_admin_by_phone(db: Session, phone: str) -> Optional[Admin]:
    """根据手机号获取管理员"""
    return db.query(Admin).filter(
        and_(Admin.phone == phone, Admin.is_del == 0)
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

def update_admin_last_login(db: Session, admin_uid: str) -> bool:
    """更新管理员最后登录时间"""
    admin = get_admin_by_uid(db, admin_uid)
    if not admin:
        return False
    
    admin.last_login_time = datetime.now()
    db.commit()
    return True

def search_admins(db: Session, username: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None, admin_id: Optional[int] = None, skip: int = 0, limit: int = 20) -> tuple[List[Admin], int]:
    """根据多个条件搜索管理员"""
    query = db.query(Admin).filter(Admin.is_del == 0)
    
    if username:
        query = query.filter(Admin.username.like(f"%{username}%"))
    if email:
        query = query.filter(Admin.email.like(f"%{email}%"))

    if phone:
        query = query.filter(Admin.phone.like(f"%{phone}%"))
    if admin_id:
        query = query.filter(Admin.id == admin_id)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    admins = query.offset(skip).limit(limit).all()
    
    return admins, total