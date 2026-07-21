from datetime import date
from sqlalchemy.orm import Session
from app.models.access_inspection import AccessInspectionRecord, AccessInspectionPhoto
from app.schemas.access_inspection import AccessInspectionRecordCreate, AccessInspectionRecordUpdate


def _gen_record_no(db: Session) -> str:
    today = date.today().strftime("%Y%m%d")
    prefix = f"A{today}"
    count = db.query(AccessInspectionRecord).filter(
        AccessInspectionRecord.record_no.like(f"{prefix}%")
    ).count()
    return f"{prefix}{count + 1:03d}"


def create_record(db: Session, data: AccessInspectionRecordCreate) -> AccessInspectionRecord:
    record = AccessInspectionRecord(record_no=_gen_record_no(db), **data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_record(db: Session, record_id: int) -> AccessInspectionRecord | None:
    return db.query(AccessInspectionRecord).filter(AccessInspectionRecord.id == record_id).first()


def list_records(db, page, page_size, location=None, inspect_date=None):
    q = db.query(AccessInspectionRecord)
    if location:
        q = q.filter(AccessInspectionRecord.location.contains(location))
    if inspect_date:
        q = q.filter(AccessInspectionRecord.inspect_date == inspect_date)
    total = q.count()
    records = (
        q.order_by(AccessInspectionRecord.inspect_date.desc(), AccessInspectionRecord.id.desc())
        .offset((page - 1) * page_size).limit(page_size).all()
    )
    return total, records


def update_record(db, record_id, data: AccessInspectionRecordUpdate):
    record = get_record(db, record_id)
    if not record:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


def delete_record(db, record_id) -> bool:
    record = get_record(db, record_id)
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


def add_photo(db, record_id, filename, original_name, filepath, thumb_filename):
    count = db.query(AccessInspectionPhoto).filter(AccessInspectionPhoto.record_id == record_id).count()
    photo = AccessInspectionPhoto(
        record_id=record_id, photo_index=count + 1,
        filename=filename, original_name=original_name,
        filepath=filepath, thumb_filename=thumb_filename,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def delete_photo(db, photo_id) -> bool:
    photo = db.query(AccessInspectionPhoto).filter(AccessInspectionPhoto.id == photo_id).first()
    if not photo:
        return False
    db.delete(photo)
    db.commit()
    return True
