from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.monitor_point import MonitorPoint

router = APIRouter()


class PointCreate(BaseModel):
    name: str
    address: Optional[str] = None
    area: Optional[str] = None


@router.get("/monitor-points", summary="获取维修点位列表")
def list_monitor_points(
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(MonitorPoint)
    if keyword:
        q = q.filter(MonitorPoint.name.like(f"%{keyword}%"))
    points = q.order_by(MonitorPoint.name).all()
    return [{"id": p.id, "name": p.name, "address": p.address, "area": p.area} for p in points]


@router.post("/monitor-points", status_code=201, summary="新增维修点位")
def create_monitor_point(
    data: PointCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    # 检查是否已存在
    exists = db.query(MonitorPoint).filter(MonitorPoint.name == data.name).first()
    if exists:
        raise HTTPException(status_code=400, detail=f"点位「{data.name}」已存在")
    point = MonitorPoint(name=data.name, address=data.address, area=data.area)
    db.add(point)
    db.commit()
    db.refresh(point)
    return {"id": point.id, "name": point.name, "address": point.address, "area": point.area}


@router.delete("/monitor-points/{point_id}", status_code=204, summary="删除维修点位")
def delete_monitor_point(
    point_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    point = db.query(MonitorPoint).filter(MonitorPoint.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="点位不存在")
    db.delete(point)
    db.commit()
