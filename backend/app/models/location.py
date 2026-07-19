from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class RepairLocation(Base):
    """维修点位库"""
    __tablename__ = "repair_locations"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(200), unique=True, nullable=False, index=True, comment="点位名称")
    address    = Column(String(300), nullable=True, comment="详细地址")
    notes      = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
