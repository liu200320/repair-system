from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ConsumableRecord(Base):
    """耗材使用记录主表"""
    __tablename__ = "consumable_records"

    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_no  = Column(String(50),  unique=True, nullable=False, comment="单号，如 C20260719001")
    location   = Column(String(200), nullable=False,              comment="耗材使用地点")
    use_date   = Column(String(20),  nullable=False,              comment="使用日期 YYYY-MM-DD")
    notes      = Column(Text,        nullable=True,               comment="备注说明")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    items  = relationship("ConsumableItem",  back_populates="record", cascade="all, delete-orphan",
                          order_by="ConsumableItem.sort_order")
    photos = relationship("ConsumablePhoto", back_populates="record", cascade="all, delete-orphan",
                          order_by="ConsumablePhoto.photo_index")


class ConsumableItem(Base):
    """耗材明细行"""
    __tablename__ = "consumable_items"

    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_id  = Column(Integer, ForeignKey("consumable_records.id", ondelete="CASCADE"), nullable=False)
    sort_order = Column(Integer, default=0, comment="行排序")
    name       = Column(String(200), nullable=False,  comment="耗材名称")
    unit       = Column(String(20),  nullable=True,   comment="单位")
    quantity   = Column(String(50),  nullable=True,   comment="数量（允许填写范围/文字）")
    signer     = Column(String(200), nullable=True,   comment="使用人签字")

    record = relationship("ConsumableRecord", back_populates="items")


class ConsumablePhoto(Base):
    """耗材现场照片"""
    __tablename__ = "consumable_photos"

    id            = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_id     = Column(Integer, ForeignKey("consumable_records.id", ondelete="CASCADE"), nullable=False)
    photo_index   = Column(Integer, default=0, comment="照片序号（1-N，用于排序和图注）")
    filename      = Column(String(255), nullable=False, comment="存储文件名")
    original_name = Column(String(255), nullable=True,  comment="原始文件名")
    filepath      = Column(String(500), nullable=False,  comment="文件相对路径")
    thumb_filename= Column(String(255), nullable=True,   comment="缩略图文件名")
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    record = relationship("ConsumableRecord", back_populates="photos")
