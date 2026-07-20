from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── 耗材明细行 ──────────────────────────────────────────────────

class ConsumableItemCreate(BaseModel):
    sort_order: int = 0
    name:       str = Field(..., max_length=200)
    unit:       Optional[str] = Field(None, max_length=20)
    quantity:   Optional[str] = Field(None, max_length=50)
    signer:     Optional[str] = Field(None, max_length=200)


class ConsumableItemRead(ConsumableItemCreate):
    id: int

    model_config = {"from_attributes": True}


# ── 照片 ────────────────────────────────────────────────────────

class ConsumablePhotoRead(BaseModel):
    id:            int
    photo_index:   int
    filename:      str
    original_name: Optional[str] = None
    filepath:      str
    thumb_filename:Optional[str] = None
    created_at:    datetime

    model_config = {"from_attributes": True}


# ── 耗材记录主表 ─────────────────────────────────────────────────

class ConsumableRecordCreate(BaseModel):
    location: str = Field(..., max_length=200)
    use_date: str = Field(..., description="使用日期 YYYY-MM-DD")
    notes:    Optional[str] = None
    items:    list[ConsumableItemCreate] = []


class ConsumableRecordUpdate(BaseModel):
    location: Optional[str] = Field(None, max_length=200)
    use_date: Optional[str] = None
    notes:    Optional[str] = None
    items:    Optional[list[ConsumableItemCreate]] = None


class ConsumableRecordRead(BaseModel):
    id:         int
    record_no:  str
    location:   str
    use_date:   str
    notes:      Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items:      list[ConsumableItemRead] = []
    photos:     list[ConsumablePhotoRead] = []

    model_config = {"from_attributes": True}


class ConsumableRecordList(BaseModel):
    """列表接口返回（不含照片详情，减少数据量）"""
    id:        int
    record_no: str
    location:  str
    use_date:  str
    notes:     Optional[str] = None
    created_at:datetime
    item_count:int = 0

    model_config = {"from_attributes": True}


class PaginatedConsumable(BaseModel):
    total: int
    page:  int
    page_size: int
    items: list[ConsumableRecordList]
