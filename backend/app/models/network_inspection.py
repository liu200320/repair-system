from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class NetworkInspectionRecord(Base):
    """网络基础设施日常巡检记录主表"""
    __tablename__ = "network_inspection_records"

    id                 = Column(Integer, primary_key=True, autoincrement=True)
    record_no          = Column(String(50), unique=True, nullable=False, comment="巡检单号，如 N20260721001")
    inspect_date       = Column(String(20), nullable=False, comment="巡检日期 YYYY-MM-DD")
    location           = Column(String(200), nullable=False, comment="巡检地点")
    inspector          = Column(String(100), nullable=True, comment="巡检人员")
    line_status        = Column(String(200), nullable=True, comment="网络线路情况")
    device_status      = Column(String(200), nullable=True, comment="接入设备情况")
    terminal_status    = Column(String(200), nullable=True, comment="终端网络情况")
    other_device       = Column(String(200), nullable=True, comment="其他设备")
    fault_description  = Column(Text, nullable=True, comment="故障描述")
    repair_content     = Column(Text, nullable=True, comment="维修内容")
    created_at         = Column(DateTime(timezone=True), server_default=func.now())
    updated_at         = Column(DateTime(timezone=True), onupdate=func.now())

    photos = relationship(
        "NetworkInspectionPhoto",
        back_populates="record",
        cascade="all, delete-orphan",
        order_by="NetworkInspectionPhoto.photo_index",
    )


class NetworkInspectionPhoto(Base):
    """网络巡检照片表"""
    __tablename__ = "network_inspection_photos"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    record_id     = Column(Integer, ForeignKey("network_inspection_records.id", ondelete="CASCADE"), nullable=False)
    photo_index   = Column(Integer, nullable=False, default=1, comment="照片序号")
    filename      = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=True)
    filepath      = Column(String(500), nullable=False)
    thumb_filename= Column(String(255), nullable=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    record = relationship("NetworkInspectionRecord", back_populates="photos")
