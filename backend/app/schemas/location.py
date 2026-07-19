from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LocationCreate(BaseModel):
    name: str
    address: Optional[str] = None
    notes: Optional[str] = None


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class LocationOut(BaseModel):
    id: int
    name: str
    address: Optional[str]
    notes: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
