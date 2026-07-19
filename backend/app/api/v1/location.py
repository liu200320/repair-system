from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.schemas.location import LocationCreate, LocationUpdate, LocationOut
from app.services import location_service

router = APIRouter()


@router.get("/locations", response_model=list[LocationOut], summary="获取点位列表")
def list_locations(
    keyword: Optional[str] = Query(None, description="名称关键字搜索"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return location_service.list_locations(db, keyword)


@router.post("/locations", response_model=LocationOut, status_code=201, summary="新建点位（仅管理员）")
def create_location(data: LocationCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return location_service.create_location(db, data)


@router.put("/locations/{loc_id}", response_model=LocationOut, summary="更新点位（仅管理员）")
def update_location(loc_id: int, data: LocationUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    obj = location_service.update_location(db, loc_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="点位不存在")
    return obj


@router.delete("/locations/{loc_id}", status_code=204, summary="删除点位（仅管理员）")
def delete_location(loc_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    ok = location_service.delete_location(db, loc_id)
    if not ok:
        raise HTTPException(status_code=404, detail="点位不存在")
