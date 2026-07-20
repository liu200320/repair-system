import os
import uuid
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
from app.schemas.consumable import (
    ConsumableRecordCreate, ConsumableRecordUpdate,
    ConsumableRecordRead, PaginatedConsumable, ConsumableRecordList,
    ConsumablePhotoRead,
)
from app.services import consumable_service
from app.services.consumable_word_export import export_consumable_to_word
from app.services.photo_processing import generate_thumbnail

router = APIRouter()

MIME_TO_EXT = {
    "image/jpeg": "jpg", "image/jpg": "jpg",
    "image/png":  "png", "image/webp": "webp",
    "image/heic": "heic", "image/heif": "heic",
}


def _save_upload(file: UploadFile) -> tuple[str, str]:
    """保存上传图片，返回 (unique_filename, full_path)"""
    ext = ""
    if file.filename and "." in file.filename:
        ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        ext = MIME_TO_EXT.get((file.content_type or "").lower(), "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型（{file.filename}，{file.content_type}），支持：jpg/png/webp/heic",
        )
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    file_path   = os.path.join(UPLOAD_DIR, unique_name)
    content     = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"文件超过限制（最大 {MAX_FILE_SIZE // 1024 // 1024}MB）")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(content)
    return unique_name, file_path


# ── 列表 / 新建 ──────────────────────────────────────────────────

@router.get("/consumables", response_model=PaginatedConsumable, summary="获取耗材记录列表")
def list_consumables(
    page:      int = Query(1,    ge=1),
    page_size: int = Query(20,   ge=1, le=100),
    location:  str = Query(None, description="按地点模糊搜索"),
    use_date:  str = Query(None, description="按使用日期精确查询 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    total, records = consumable_service.list_records(db, page, page_size, location, use_date)
    items = [
        ConsumableRecordList(
            id=r.id, record_no=r.record_no, location=r.location,
            use_date=r.use_date, notes=r.notes, created_at=r.created_at,
            item_count=len(r.items),
        )
        for r in records
    ]
    return PaginatedConsumable(total=total, page=page, page_size=page_size, items=items)


@router.post("/consumables", response_model=ConsumableRecordRead, status_code=201, summary="新建耗材记录")
def create_consumable(
    data: ConsumableRecordCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return consumable_service.create_record(db, data)


# ── 单条操作 ─────────────────────────────────────────────────────

@router.get("/consumables/{record_id}", response_model=ConsumableRecordRead, summary="获取耗材记录详情")
def get_consumable(record_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    record = consumable_service.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.put("/consumables/{record_id}", response_model=ConsumableRecordRead, summary="更新耗材记录")
def update_consumable(
    record_id: int,
    data: ConsumableRecordUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    record = consumable_service.update_record(db, record_id, data)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.delete("/consumables/{record_id}", status_code=204, summary="删除耗材记录")
def delete_consumable(record_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if not consumable_service.delete_record(db, record_id):
        raise HTTPException(status_code=404, detail="记录不存在")


# ── 照片上传 / 删除 ───────────────────────────────────────────────

@router.post(
    "/consumables/{record_id}/photos",
    response_model=ConsumablePhotoRead,
    status_code=201,
    summary="上传耗材现场照片",
)
def upload_consumable_photo(
    record_id: int,
    file: UploadFile = File(..., description="图片文件（jpg/png/webp/heic）"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    record = consumable_service.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="耗材记录不存在")

    unique_name, file_path = _save_upload(file)
    thumb_name = generate_thumbnail(file_path)

    photo = consumable_service.add_photo(
        db,
        record_id=record_id,
        filename=unique_name,
        original_name=file.filename,
        filepath=file_path,
        thumb_filename=thumb_name or None,
    )
    return photo


@router.delete(
    "/consumables/{record_id}/photos/{photo_id}",
    status_code=204,
    summary="删除耗材照片",
)
def delete_consumable_photo(
    record_id: int, photo_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    if not consumable_service.delete_photo(db, photo_id):
        raise HTTPException(status_code=404, detail="照片不存在")


# ── Word 导出 ────────────────────────────────────────────────────

@router.post(
    "/consumables/{record_id}/export",
    summary="导出耗材使用情况表为 Word",
)
def export_consumable(
    record_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    record = consumable_service.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    out_dir     = os.path.join("uploads", "exports")
    os.makedirs(out_dir, exist_ok=True)
    dl_name     = f"耗材使用情况表_{record.record_no}.docx"
    output_path = os.path.join(out_dir, dl_name)

    try:
        export_consumable_to_word(record, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败：{str(e)}")

    return FileResponse(
        path=output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=dl_name,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(dl_name)}"},
    )
