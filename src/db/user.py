from sqlalchemy import Column, Integer, String, func, TIMESTAMP
from sqlalchemy.dialects.mysql import TINYINT
from db.database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, index=True, nullable=False, comment='用户名')
    email = Column(String(100), unique=True, index=True, nullable=False, comment='邮箱')
    password_hash = Column(String(255), nullable=False, comment='密码哈希')
    phone = Column(String(20), nullable=True, comment='手机号')

    is_del = Column(TINYINT, default=0, comment='是否删除：0-未删除，1-已删除')
    created_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    last_login_time = Column(TIMESTAMP, nullable=True, comment='最后登录时间')

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

