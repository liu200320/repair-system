import os
import uuid
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
from app.schemas.network_inspection import (
    NetworkInspectionRecordCreate, NetworkInspectionRecordUpdate,
    NetworkInspectionRecordRead, PaginatedNetworkInspection, NetworkInspectionRecordList,
    NetworkInspectionPhotoRead,
)
from app.services import network_inspection_service
from app.services.network_inspection_word_export import (
    export_network_inspection_to_word,
    export_network_inspection_range_to_word,
)
from app.services.photo_processing import generate_thumbnail

router = APIRouter()

MIME_TO_EXT = {
    "image/jpeg": "jpg", "image/jpg": "jpg",
    "image/png":  "png", "image/webp": "webp",
    "image/heic": "heic", "image/heif": "heic",
}


def _save_upload(file: UploadFile) -> tuple[str, str]:
    ext = ""
    if file.filename and "." in file.filename:
        ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        ext = MIME_TO_EXT.get((file.content_type or "").lower(), "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型，支持：jpg/png/webp/heic")
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

@router.get("/network-inspections", response_model=PaginatedNetworkInspection, summary="获取巡检记录列表")
def list_network_inspections(
    page:         int = Query(1,    ge=1),
    page_size:    int = Query(20,   ge=1, le=100),
    location:     str = Query(None, description="按地点模糊搜索"),
    inspect_date: str = Query(None, description="按巡检日期精确查询 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    total, records = network_inspection_service.list_records(db, page, page_size, location, inspect_date)
    items = [NetworkInspectionRecordList.model_validate(r) for r in records]
    return PaginatedNetworkInspection(total=total, page=page, page_size=page_size, items=items)


@router.post("/network-inspections", response_model=NetworkInspectionRecordRead, status_code=201, summary="新建巡检记录")
def create_network_inspection(
    data: NetworkInspectionRecordCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return network_inspection_service.create_record(db, data)


# ── 单条操作 ─────────────────────────────────────────────────────

@router.get("/network-inspections/{record_id}", response_model=NetworkInspectionRecordRead, summary="获取巡检记录详情")
def get_network_inspection(record_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    record = network_inspection_service.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.put("/network-inspections/{record_id}", response_model=NetworkInspectionRecordRead, summary="更新巡检记录")
def update_network_inspection(
    record_id: int,
    data: NetworkInspectionRecordUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    record = network_inspection_service.update_record(db, record_id, data)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.delete("/network-inspections/{record_id}", status_code=204, summary="删除巡检记录")
def delete_network_inspection(record_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if not network_inspection_service.delete_record(db, record_id):
        raise HTTPException(status_code=404, detail="记录不存在")


# ── 照片上传 / 删除 ───────────────────────────────────────────────

@router.post(
    "/network-inspections/{record_id}/photos",
    response_model=NetworkInspectionPhotoRead,
    status_code=201,
    summary="上传巡检现场照片",
)
def upload_network_inspection_photo(
    record_id: int,
    file: UploadFile = File(..., description="图片文件（jpg/png/webp/heic）"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    record = network_inspection_service.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="巡检记录不存在")
    unique_name, file_path = _save_upload(file)
    thumb_name = generate_thumbnail(file_path)
    photo = network_inspection_service.add_photo(
        db, record_id=record_id,
        filename=unique_name, original_name=file.filename,
        filepath=file_path, thumb_filename=thumb_name or None,
    )
    return photo


@router.delete(
    "/network-inspections/{record_id}/photos/{photo_id}",
    status_code=204,
    summary="删除巡检照片",
)
def delete_network_inspection_photo(
    record_id: int, photo_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    if not network_inspection_service.delete_photo(db, photo_id):
        raise HTTPException(status_code=404, detail="照片不存在")


# ── Word 导出 ────────────────────────────────────────────────────

@router.post(
    "/network-inspections/{record_id}/export",
    summary="导出巡检记录为 Word",
)
def export_network_inspection(
    record_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    record = network_inspection_service.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    out_dir     = os.path.join("uploads", "exports")
    os.makedirs(out_dir, exist_ok=True)
    dl_name     = f"网络基础设施巡检表_{record.record_no}.docx"
    output_path = os.path.join(out_dir, dl_name)

    try:
        export_network_inspection_to_word(record, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败：{str(e)}")

    return FileResponse(
        path=output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=dl_name,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(dl_name)}"},
    )


# ── 获取可选地点列表 ────────────────────────────────────────────

@router.get("/network-inspections-locations", summary="获取网络基础设施地点列表（下拉用）")
def get_network_locations(db: Session = Depends(get_db), _=Depends(get_current_user)):
    from app.models.network_location import NetworkLocation
    locs = db.query(NetworkLocation).order_by(NetworkLocation.id).all()
    return [{"id": l.id, "name": l.name} for l in locs]


# ── 网络巡检点位管理 CRUD ────────────────────────────────────

@router.get("/network-locations", summary="网络巡检点位列表（管理）")
def list_network_locations(
    keyword: str = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    from app.models.network_location import NetworkLocation
    q = db.query(NetworkLocation)
    if keyword:
        q = q.filter(NetworkLocation.name.like(f"%{keyword}%"))
    locs = q.order_by(NetworkLocation.name).all()
    return [{"id": l.id, "name": l.name} for l in locs]


@router.post("/network-locations", status_code=201, summary="新增网络巡检点位")
def create_network_location(
    data: dict,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    from app.models.network_location import NetworkLocation
    from pydantic import BaseModel
    name = data.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="点位名称不能为空")
    if db.query(NetworkLocation).filter(NetworkLocation.name == name).first():
        raise HTTPException(status_code=400, detail=f"点位「{name}」已存在")
    loc = NetworkLocation(name=name)
    db.add(loc); db.commit(); db.refresh(loc)
    return {"id": loc.id, "name": loc.name}


@router.delete("/network-locations/{loc_id}", status_code=204, summary="删除网络巡检点位")
def delete_network_location(loc_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    from app.models.network_location import NetworkLocation
    loc = db.query(NetworkLocation).filter(NetworkLocation.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="点位不存在")
    db.delete(loc); db.commit()


# ── 时间段批量导出 ────────────────────────────────────────────

@router.get(
    "/network-inspections/export/range",
    summary="按日期范围批量导出巡检记录为 Word",
)
def export_network_inspection_range(
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date:   str = Query(..., description="结束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    _, records = network_inspection_service.list_records(db, page=1, page_size=500)
    records = [r for r in records if start_date <= r.inspect_date <= end_date]
    records.sort(key=lambda r: r.inspect_date)

    if not records:
        raise HTTPException(status_code=404, detail=f"{start_date} 至 {end_date} 没有巡检记录")

    out_dir     = os.path.join("uploads", "exports")
    os.makedirs(out_dir, exist_ok=True)
    filename    = f"网络巡检汇总_{start_date}_至_{end_date}.docx"
    output_path = os.path.join(out_dir, filename)

    try:
        export_network_inspection_range_to_word(records, start_date, end_date, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败：{str(e)}")

    return FileResponse(
        path=output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"},
    )
