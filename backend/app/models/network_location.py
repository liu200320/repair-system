from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class NetworkLocation(Base):
    """网络基础设施巡检地点库"""
    __tablename__ = "network_locations"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(200), unique=True, nullable=False, index=True, comment="地点名称")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
