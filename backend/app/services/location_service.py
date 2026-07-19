from sqlalchemy.orm import Session
from app.models.location import RepairLocation
from app.schemas.location import LocationCreate, LocationUpdate
from typing import Optional


def list_locations(db: Session, keyword: Optional[str] = None):
    q = db.query(RepairLocation)
    if keyword:
        q = q.filter(RepairLocation.name.like(f"%{keyword}%"))
    return q.order_by(RepairLocation.name).all()


def get_location(db: Session, loc_id: int):
    return db.query(RepairLocation).filter(RepairLocation.id == loc_id).first()


def create_location(db: Session, data: LocationCreate):
    obj = RepairLocation(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_location(db: Session, loc_id: int, data: LocationUpdate):
    obj = get_location(db, loc_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_location(db: Session, loc_id: int) -> bool:
    obj = get_location(db, loc_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
