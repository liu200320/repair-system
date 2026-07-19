from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class RepairStatus(str, enum.Enum):
    pending = "pending"       # 待维修
    in_progress = "in_progress"  # 维修中
    completed = "completed"   # 已完成


class PhotoPhase(str, enum.Enum):
    before = "before"   # 维修前
    during = "during"   # 维修中
    after = "after"     # 维修后


class RepairRecord(Base):
    """维修记录主表"""
    __tablename__ = "repair_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_no = Column(String(50), unique=True, nullable=False, comment="工单编号，如 R20260719001")
    repair_date = Column(String(20), nullable=False, comment="维修日期 YYYY-MM-DD")
    location = Column(String(200), nullable=False, comment="维修点位")
    description = Column(Text, nullable=True, comment="故障描述")
    repair_content = Column(Text, nullable=True, comment="维修内容")
    repairer = Column(String(50), nullable=True, comment="维修人员")
    status = Column(Enum(RepairStatus), default=RepairStatus.pending, comment="状态")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联照片
    photos = relationship("RepairPhoto", back_populates="repair", cascade="all, delete-orphan")


class RepairPhoto(Base):
    """维修照片表"""
    __tablename__ = "repair_photos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    repair_id = Column(Integer, ForeignKey("repair_records.id", ondelete="CASCADE"), nullable=False)
    phase = Column(Enum(PhotoPhase), nullable=False, comment="维修阶段：before/during/after")
    filename = Column(String(255), nullable=False, comment="存储文件名")
    original_name = Column(String(255), nullable=True, comment="原始文件名")
    filepath = Column(String(500), nullable=False, comment="文件相对路径")
    thumb_filename = Column(String(255), nullable=True, comment="缩略图文件名")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    repair = relationship("RepairRecord", back_populates="photos")
