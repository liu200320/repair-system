from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class AccessLocation(Base):
    """门禁巡检地点库"""
    __tablename__ = "access_locations"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(200), unique=True, nullable=False, index=True, comment="门禁地点名称")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
