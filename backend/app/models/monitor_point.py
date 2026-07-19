from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class MonitorPoint(Base):
    """监控/维修点位表（monitor_points），由外部维护，系统只读"""
    __tablename__ = "monitor_points"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(200), nullable=False, unique=True, index=True)
    address    = Column(String(300), nullable=True)
    area       = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
