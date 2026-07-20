from datetime import date
from sqlalchemy.orm import Session
from app.models.consumable import ConsumableRecord, ConsumableItem, ConsumablePhoto
from app.schemas.consumable import ConsumableRecordCreate, ConsumableRecordUpdate


def _gen_record_no(db: Session) -> str:
    """生成单号，格式 C{YYYYMMDD}{3位序号}，如 C20260718001"""
    today = date.today().strftime("%Y%m%d")
    prefix = f"C{today}"
    count = db.query(ConsumableRecord).filter(
        ConsumableRecord.record_no.like(f"{prefix}%")
    ).count()
    return f"{prefix}{count + 1:03d}"


# ── CRUD ────────────────────────────────────────────────────────

def create_record(db: Session, data: ConsumableRecordCreate) -> ConsumableRecord:
    record = ConsumableRecord(
        record_no=_gen_record_no(db),
        location=data.location,
        use_date=data.use_date,
        notes=data.notes,
    )
    db.add(record)
    db.flush()  # 获取 id，在提交前关联明细

    for idx, item_data in enumerate(data.items):
        item = ConsumableItem(
            record_id=record.id,
            sort_order=item_data.sort_order if item_data.sort_order else idx,
            name=item_data.name,
            unit=item_data.unit,
            quantity=item_data.quantity,
            signer=item_data.signer,
        )
        db.add(item)

    db.commit()
    db.refresh(record)
    return record


def get_record(db: Session, record_id: int) -> ConsumableRecord | None:
    return db.query(ConsumableRecord).filter(ConsumableRecord.id == record_id).first()


def list_records(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    location: str | None = None,
    use_date: str | None = None,
) -> tuple[int, list[ConsumableRecord]]:
    q = db.query(ConsumableRecord)
    if location:
        q = q.filter(ConsumableRecord.location.contains(location))
    if use_date:
        q = q.filter(ConsumableRecord.use_date == use_date)
    total = q.count()
    records = q.order_by(ConsumableRecord.use_date.desc(), ConsumableRecord.id.desc()) \
               .offset((page - 1) * page_size).limit(page_size).all()
    return total, records


def update_record(db: Session, record_id: int, data: ConsumableRecordUpdate) -> ConsumableRecord | None:
    record = get_record(db, record_id)
    if not record:
        return None

    if data.location is not None:
        record.location = data.location
    if data.use_date is not None:
        record.use_date = data.use_date
    if data.notes is not None:
        record.notes = data.notes

    # 如果传入了 items，整体替换（先删后增）
    if data.items is not None:
        db.query(ConsumableItem).filter(ConsumableItem.record_id == record_id).delete()
        for idx, item_data in enumerate(data.items):
            item = ConsumableItem(
                record_id=record_id,
                sort_order=item_data.sort_order if item_data.sort_order else idx,
                name=item_data.name,
                unit=item_data.unit,
                quantity=item_data.quantity,
                signer=item_data.signer,
            )
            db.add(item)

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


# ── 照片相关 ─────────────────────────────────────────────────────

def add_photo(
    db: Session,
    record_id: int,
    filename: str,
    original_name: str,
    filepath: str,
    thumb_filename: str | None = None,
) -> ConsumablePhoto:
    # 当前最大序号 + 1
    max_idx = db.query(ConsumablePhoto).filter(
        ConsumablePhoto.record_id == record_id
    ).count()
    photo = ConsumablePhoto(
        record_id=record_id,
        photo_index=max_idx + 1,
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
    photo = db.query(ConsumablePhoto).filter(ConsumablePhoto.id == photo_id).first()
    if not photo:
        return False
    db.delete(photo)
    db.commit()
    return True
