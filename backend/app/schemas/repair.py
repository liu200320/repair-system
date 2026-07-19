from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.repair import RepairStatus, PhotoPhase


# ---------- 照片 ----------

class PhotoOut(BaseModel):
    id: int
    phase: PhotoPhase
    filename: str
    original_name: Optional[str]
    filepath: str
    thumb_filename: Optional[str] = None
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------- 维修记录 ----------

class RepairCreate(BaseModel):
    repair_date: str = Field(..., example="2026-07-19", description="维修日期 YYYY-MM-DD")
    location: str = Field(..., max_length=200, description="维修点位")
    description: Optional[str] = Field(None, description="故障描述")
    repair_content: Optional[str] = Field(None, description="维修内容")
    repairer: Optional[str] = Field(None, max_length=50, description="维修人员")
    status: RepairStatus = RepairStatus.pending


class RepairUpdate(BaseModel):
    repair_date: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    repair_content: Optional[str] = None
    repairer: Optional[str] = None
    status: Optional[RepairStatus] = None


class RepairOut(BaseModel):
    id: int
    record_no: str
    repair_date: str
    location: str
    description: Optional[str]
    repair_content: Optional[str]
    repairer: Optional[str]
    status: RepairStatus
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    photos: List[PhotoOut] = []

    class Config:
        from_attributes = True


class RepairList(BaseModel):
    total: int
    items: List[RepairOut]
