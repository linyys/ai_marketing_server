from sqlalchemy import Column, Integer, String, func, TIMESTAMP, Boolean, Index, CheckConstraint
from sqlalchemy.dialects.mysql import TINYINT
from db.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()), comment='用户唯一标识')
    username = Column(String(50), unique=True, index=True, nullable=False, comment='用户名')
    email = Column(String(100), unique=True, index=True, nullable=False, comment='邮箱')
    password_hash = Column(String(255), nullable=False, comment='密码哈希')
    phone = Column(String(20), nullable=True, comment='手机号')
    is_del = Column(TINYINT(1), nullable=False, default=False, comment='是否删除：0-未删除，1-已删除')
    created_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), comment='创建时间')
    updated_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    last_login_time = Column(TIMESTAMP, nullable=True, comment='最后登录时间')
    
    __table_args__ = (
        Index('idx_is_del', 'is_del'),
        Index('idx_created_time', 'created_time'),
        Index('idx_last_login_time', 'last_login_time'),
        CheckConstraint('is_del IN (0, 1)', name='chk_is_del'),
        CheckConstraint('LENGTH(username) >= 3', name='chk_username_length'),
        CheckConstraint('email LIKE "%@%"', name='chk_email_format'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

