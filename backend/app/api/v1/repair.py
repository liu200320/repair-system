from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.schemas.repair import RepairCreate, RepairUpdate, RepairOut, RepairList
from app.services import repair_service

router = APIRouter()


@router.get("/repairs", response_model=RepairList, summary="获取维修记录列表")
def list_repairs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    location: Optional[str] = Query(None),
    repair_date: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),          # 登录即可查看
):
    total, items = repair_service.list_repairs(db, page, page_size, location, repair_date, status)
    return {"total": total, "items": items}


@router.post("/repairs", response_model=RepairOut, status_code=201, summary="新建维修记录")
def create_repair(data: RepairCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return repair_service.create_repair(db, data)


@router.get("/repairs/{repair_id}", response_model=RepairOut, summary="获取单条维修记录")
def get_repair(repair_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = repair_service.get_repair(db, repair_id)
    if not obj:
        raise HTTPException(status_code=404, detail="记录不存在")
    return obj


@router.put("/repairs/{repair_id}", response_model=RepairOut, summary="更新维修记录")
def update_repair(repair_id: int, data: RepairUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    obj = repair_service.update_repair(db, repair_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="记录不存在")
    return obj


@router.delete("/repairs/{repair_id}", status_code=204, summary="删除维修记录")
def delete_repair(repair_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):  # 仅管理员可删
    ok = repair_service.delete_repair(db, repair_id)
    if not ok:
        raise HTTPException(status_code=404, detail="记录不存在")
