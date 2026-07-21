import os
import uuid
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
from app.schemas.access_inspection import (
    AccessInspectionRecordCreate, AccessInspectionRecordUpdate,
    AccessInspectionRecordRead, PaginatedAccessInspection,
    AccessInspectionRecordList, AccessInspectionPhotoRead,
)
from app.services import access_inspection_service
from app.services.access_inspection_word_export import (
    export_access_inspection_to_word,
    export_access_inspection_range_to_word,
)
from app.services.photo_processing import generate_thumbnail

router = APIRouter()

MIME_TO_EXT = {
    "image/jpeg": "jpg", "image/jpg": "jpg",
    "image/png": "png", "image/webp": "webp",
    "image/heic": "heic", "image/heif": "heic",
}


def _save_upload(file: UploadFile) -> tuple[str, str]:
    ext = ""
    if file.filename and "." in file.filename:
        ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        ext = MIME_TO_EXT.get((file.content_type or "").lower(), "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不支持的文件类型，支持：jpg/png/webp/heic")
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"文件超过限制（最大 {MAX_FILE_SIZE // 1024 // 1024}MB）")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(content)
    return unique_name, file_path


@router.get("/access-inspections", response_model=PaginatedAccessInspection, summary="获取门禁巡检记录列表")
def list_access_inspections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    location: str = Query(None),
    inspect_date: str = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    total, records = access_inspection_service.list_records(db, page, page_size, location, inspect_date)
    items = [AccessInspectionRecordList.model_validate(r) for r in records]
    return PaginatedAccessInspection(total=total, page=page, page_size=page_size, items=items)


@router.post("/access-inspections", response_model=AccessInspectionRecordRead, status_code=201, summary="新建门禁巡检记录")
def create_access_inspection(data: AccessInspectionRecordCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return access_inspection_service.create_record(db, data)


@router.get("/access-inspections/export/range", summary="按日期范围批量导出门禁巡检记录为 Word")
def export_access_inspection_range(
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    _, records = access_inspection_service.list_records(db, page=1, page_size=500)
    records = [r for r in records if start_date <= r.inspect_date <= end_date]
    records.sort(key=lambda r: r.inspect_date)
    if not records:
        raise HTTPException(status_code=404, detail=f"{start_date} 至 {end_date} 没有门禁巡检记录")
    out_dir = os.path.join("uploads", "exports")
    os.makedirs(out_dir, exist_ok=True)
    filename = f"门禁巡检汇总_{start_date}_至_{end_date}.docx"
    output_path = os.path.join(out_dir, filename)
    try:
        export_access_inspection_range_to_word(records, start_date, end_date, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败：{str(e)}")
    return FileResponse(
        path=output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"},
    )


@router.get("/access-inspections/{record_id}", response_model=AccessInspectionRecordRead, summary="获取门禁巡检记录详情")
def get_access_inspection(record_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    record = access_inspection_service.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.put("/access-inspections/{record_id}", response_model=AccessInspectionRecordRead, summary="更新门禁巡检记录")
def update_access_inspection(record_id: int, data: AccessInspectionRecordUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    record = access_inspection_service.update_record(db, record_id, data)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.delete("/access-inspections/{record_id}", status_code=204, summary="删除门禁巡检记录")
def delete_access_inspection(record_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if not access_inspection_service.delete_record(db, record_id):
        raise HTTPException(status_code=404, detail="记录不存在")


@router.post("/access-inspections/{record_id}/photos", response_model=AccessInspectionPhotoRead, status_code=201, summary="上传门禁巡检照片")
def upload_access_inspection_photo(
    record_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    record = access_inspection_service.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="巡检记录不存在")
    unique_name, file_path = _save_upload(file)
    thumb_name = generate_thumbnail(file_path)
    return access_inspection_service.add_photo(db, record_id=record_id, filename=unique_name,
        original_name=file.filename, filepath=file_path, thumb_filename=thumb_name or None)


@router.delete("/access-inspections/{record_id}/photos/{photo_id}", status_code=204, summary="删除门禁巡检照片")
def delete_access_inspection_photo(record_id: int, photo_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if not access_inspection_service.delete_photo(db, photo_id):
        raise HTTPException(status_code=404, detail="照片不存在")


@router.post("/access-inspections/{record_id}/export", summary="导出单条门禁巡检记录为 Word")
def export_access_inspection(record_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    record = access_inspection_service.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    out_dir = os.path.join("uploads", "exports")
    os.makedirs(out_dir, exist_ok=True)
    dl_name = f"门禁日常巡检表_{record.record_no}.docx"
    output_path = os.path.join(out_dir, dl_name)
    try:
        export_access_inspection_to_word(record, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败：{str(e)}")
    return FileResponse(
        path=output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=dl_name,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(dl_name)}"},
    )


@router.get("/access-inspections-locations", summary="获取门禁地点列表（下拉用）")
def get_access_locations(db: Session = Depends(get_db), _=Depends(get_current_user)):
    from app.models.access_location import AccessLocation
    locs = db.query(AccessLocation).order_by(AccessLocation.id).all()
    return [{"id": l.id, "name": l.name} for l in locs]


# ── 门禁点位管理 CRUD ─────────────────────────────────────────

@router.get("/access-locations", summary="门禁点位列表（管理）")
def list_access_locations(
    keyword: str = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    from app.models.access_location import AccessLocation
    q = db.query(AccessLocation)
    if keyword:
        q = q.filter(AccessLocation.name.like(f"%{keyword}%"))
    locs = q.order_by(AccessLocation.name).all()
    return [{"id": l.id, "name": l.name} for l in locs]


@router.post("/access-locations", status_code=201, summary="新增门禁点位")
def create_access_location(
    data: dict,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    from app.models.access_location import AccessLocation
    name = data.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="点位名称不能为空")
    if db.query(AccessLocation).filter(AccessLocation.name == name).first():
        raise HTTPException(status_code=400, detail=f"点位「{name}」已存在")
    loc = AccessLocation(name=name)
    db.add(loc); db.commit(); db.refresh(loc)
    return {"id": loc.id, "name": loc.name}


@router.delete("/access-locations/{loc_id}", status_code=204, summary="删除门禁点位")
def delete_access_location(loc_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    from app.models.access_location import AccessLocation
    loc = db.query(AccessLocation).filter(AccessLocation.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="点位不存在")
    db.delete(loc); db.commit()
