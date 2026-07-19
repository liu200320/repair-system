from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from app.models.repair import RepairRecord, RepairPhoto, PhotoPhase
from app.schemas.repair import RepairCreate, RepairUpdate
from datetime import date


def _gen_record_no(db: Session) -> str:
    """生成工单编号，格式：R + 日期 + 3位序号，如 R202607190001"""
    today = date.today().strftime("%Y%m%d")
    prefix = f"R{today}"
    last = (
        db.query(RepairRecord)
        .filter(RepairRecord.record_no.like(f"{prefix}%"))
        .order_by(desc(RepairRecord.record_no))
        .first()
    )
    if last:
        seq = int(last.record_no[len(prefix):]) + 1
    else:
        seq = 1
    return f"{prefix}{seq:04d}"


def create_repair(db: Session, data: RepairCreate) -> RepairRecord:
    record_no = _gen_record_no(db)
    obj = RepairRecord(record_no=record_no, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_repair(db: Session, repair_id: int) -> Optional[RepairRecord]:
    return db.query(RepairRecord).filter(RepairRecord.id == repair_id).first()


def list_repairs(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    location: Optional[str] = None,
    repair_date: Optional[str] = None,
    status: Optional[str] = None,
):
    q = db.query(RepairRecord)
    if location:
        q = q.filter(RepairRecord.location.like(f"%{location}%"))
    if repair_date:
        q = q.filter(RepairRecord.repair_date == repair_date)
    if status:
        q = q.filter(RepairRecord.status == status)
    total = q.count()
    items = q.order_by(desc(RepairRecord.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    return total, items


def update_repair(db: Session, repair_id: int, data: RepairUpdate) -> Optional[RepairRecord]:
    obj = get_repair(db, repair_id)
    if not obj:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_repair(db: Session, repair_id: int) -> bool:
    obj = get_repair(db, repair_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def add_photo(
    db: Session,
    repair_id: int,
    phase: PhotoPhase,
    filename: str,
    original_name: str,
    filepath: str,
    thumb_filename: str = None,
) -> RepairPhoto:
    photo = RepairPhoto(
        repair_id=repair_id,
        phase=phase,
        filename=filename,
        original_name=original_name,
        filepath=filepath,
        thumb_filename=thumb_filename,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def delete_photo(db: Session, photo_id: int) -> bool:
    photo = db.query(RepairPhoto).filter(RepairPhoto.id == photo_id).first()
    if not photo:
        return False
    db.delete(photo)
    db.commit()
    return True
