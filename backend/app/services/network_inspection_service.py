from datetime import date
from sqlalchemy.orm import Session
from app.models.network_inspection import NetworkInspectionRecord, NetworkInspectionPhoto
from app.schemas.network_inspection import NetworkInspectionRecordCreate, NetworkInspectionRecordUpdate


def _gen_record_no(db: Session) -> str:
    today = date.today().strftime("%Y%m%d")
    prefix = f"N{today}"
    count = db.query(NetworkInspectionRecord).filter(
        NetworkInspectionRecord.record_no.like(f"{prefix}%")
    ).count()
    return f"{prefix}{count + 1:03d}"


def create_record(db: Session, data: NetworkInspectionRecordCreate) -> NetworkInspectionRecord:
    record = NetworkInspectionRecord(
        record_no=_gen_record_no(db),
        **data.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_record(db: Session, record_id: int) -> NetworkInspectionRecord | None:
    return db.query(NetworkInspectionRecord).filter(NetworkInspectionRecord.id == record_id).first()


def list_records(
    db: Session, page: int, page_size: int,
    location: str | None = None, inspect_date: str | None = None,
):
    q = db.query(NetworkInspectionRecord)
    if location:
        q = q.filter(NetworkInspectionRecord.location.contains(location))
    if inspect_date:
        q = q.filter(NetworkInspectionRecord.inspect_date == inspect_date)
    total = q.count()
    records = (
        q.order_by(NetworkInspectionRecord.inspect_date.desc(), NetworkInspectionRecord.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, records


def update_record(db: Session, record_id: int, data: NetworkInspectionRecordUpdate) -> NetworkInspectionRecord | None:
    record = get_record(db, record_id)
    if not record:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


def delete_record(db: Session, record_id: int) -> bool:
    record = get_record(db, record_id)
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


def add_photo(
    db: Session, record_id: int,
    filename: str, original_name: str, filepath: str, thumb_filename: str | None,
) -> NetworkInspectionPhoto:
    count = db.query(NetworkInspectionPhoto).filter(NetworkInspectionPhoto.record_id == record_id).count()
    photo = NetworkInspectionPhoto(
        record_id=record_id,
        photo_index=count + 1,
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
    photo = db.query(NetworkInspectionPhoto).filter(NetworkInspectionPhoto.id == photo_id).first()
    if not photo:
        return False
    db.delete(photo)
    db.commit()
    return True
