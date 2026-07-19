from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.repair import RepairRecord, RepairStatus
from datetime import date, timedelta

router = APIRouter()


@router.get("/stats/summary", summary="状态汇总")
def summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.query(RepairRecord.status, func.count(RepairRecord.id)).group_by(RepairRecord.status).all()
    status_map = {"pending": "待维修", "in_progress": "维修中", "completed": "已完成"}
    result = {s: 0 for s in status_map}
    for status, cnt in rows:
        result[status.value] = cnt
    result["total"] = sum(result.values())
    result["labels"] = status_map
    return result


@router.get("/stats/trend", summary="近30天每日维修数量趋势")
def trend(db: Session = Depends(get_db), _=Depends(get_current_user)):
    today = date.today()
    days = [(today - timedelta(days=i)).isoformat() for i in range(29, -1, -1)]

    rows = (
        db.query(RepairRecord.repair_date, func.count(RepairRecord.id))
        .filter(RepairRecord.repair_date >= days[0])
        .group_by(RepairRecord.repair_date)
        .all()
    )
    date_map = {d: cnt for d, cnt in rows}
    return {
        "dates":  days,
        "counts": [date_map.get(d, 0) for d in days],
    }


@router.get("/stats/locations", summary="维修次数最多的前10个点位")
def top_locations(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = (
        db.query(RepairRecord.location, func.count(RepairRecord.id).label("cnt"))
        .group_by(RepairRecord.location)
        .order_by(desc("cnt"))
        .limit(10)
        .all()
    )
    return {"names": [r.location for r in rows], "counts": [r.cnt for r in rows]}
