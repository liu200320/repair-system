from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """系统用户表"""
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username   = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    hashed_pw  = Column(String(200), nullable=False, comment="bcrypt 哈希密码")
    full_name  = Column(String(50), nullable=True, comment="姓名")
    role       = Column(String(20), default="viewer", comment="admin=管理员 viewer=只读")
    is_active  = Column(Boolean, default=True, comment="账号是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
