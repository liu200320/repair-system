from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AccessInspectionPhotoRead(BaseModel):
    id:            int
    photo_index:   int
    filename:      str
    original_name: Optional[str] = None
    filepath:      str
    thumb_filename:Optional[str] = None
    created_at:    datetime
    model_config = {"from_attributes": True}


class AccessInspectionRecordCreate(BaseModel):
    inspect_date:      str = Field(..., description="巡检日期 YYYY-MM-DD")
    location:          str = Field(..., max_length=200)
    inspector:         Optional[str] = Field(None, max_length=100)
    gate_status:       Optional[str] = Field(None, max_length=200)
    flap_status:       Optional[str] = Field(None, max_length=200)
    system_status:     Optional[str] = Field(None, max_length=200)
    other_device:      Optional[str] = Field(None, max_length=200)
    fault_description: Optional[str] = None
    repair_content:    Optional[str] = None


class AccessInspectionRecordUpdate(BaseModel):
    inspect_date:      Optional[str] = None
    location:          Optional[str] = Field(None, max_length=200)
    inspector:         Optional[str] = Field(None, max_length=100)
    gate_status:       Optional[str] = Field(None, max_length=200)
    flap_status:       Optional[str] = Field(None, max_length=200)
    system_status:     Optional[str] = Field(None, max_length=200)
    other_device:      Optional[str] = Field(None, max_length=200)
    fault_description: Optional[str] = None
    repair_content:    Optional[str] = None


class AccessInspectionRecordRead(BaseModel):
    id:               int
    record_no:        str
    inspect_date:     str
    location:         str
    inspector:        Optional[str] = None
    gate_status:      Optional[str] = None
    flap_status:      Optional[str] = None
    system_status:    Optional[str] = None
    other_device:     Optional[str] = None
    fault_description:Optional[str] = None
    repair_content:   Optional[str] = None
    created_at:       datetime
    updated_at:       Optional[datetime] = None
    photos:           list[AccessInspectionPhotoRead] = []
    model_config = {"from_attributes": True}


class AccessInspectionRecordList(BaseModel):
    id:           int
    record_no:    str
    inspect_date: str
    location:     str
    inspector:    Optional[str] = None
    created_at:   datetime
    model_config = {"from_attributes": True}


class PaginatedAccessInspection(BaseModel):
    total:     int
    page:      int
    page_size: int
    items:     list[AccessInspectionRecordList]
