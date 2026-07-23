import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
from app.core.security import get_current_user
from app.models.repair import PhotoPhase
from app.schemas.repair import PhotoOut
from app.services import repair_service
from app.services.photo_processing import generate_thumbnail, apply_watermark

router = APIRouter()


MIME_TO_EXT = {
    "image/jpeg": "jpg",
    "image/jpg":  "jpg",
    "image/png":  "png",
    "image/webp": "webp",
    "image/heic": "heic",
    "image/heif": "heic",
}


def _save_file(upload_file: UploadFile) -> tuple[str, str]:
    """保存上传文件，返回 (存储文件名, 相对路径)"""
    ext = ""
    if upload_file.filename and "." in upload_file.filename:
        ext = upload_file.filename.rsplit(".", 1)[-1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        ext = MIME_TO_EXT.get((upload_file.content_type or "").lower(), "")

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型（文件名：{upload_file.filename}，"
                   f"类型：{upload_file.content_type}），支持：jpg / jpeg / png / webp / heic",
        )

    # 分块读取，超出限制立即中断，避免内存耗尽
    chunks = []
    size = 0
    chunk_size = 64 * 1024  # 64KB per chunk
    while True:
        chunk = upload_file.file.read(chunk_size)
        if not chunk:
            break
        size += len(chunk)
        if size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"文件超过限制（最大 {MAX_FILE_SIZE // 1024 // 1024}MB）")
        chunks.append(chunk)
    content = b"".join(chunks)

    unique_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(content)

    return unique_name, file_path


@router.post(
    "/repairs/{repair_id}/photos",
    response_model=PhotoOut,
    status_code=201,
    summary="上传维修照片",
)
def upload_photo(
    repair_id: int,
    phase: PhotoPhase = Form(..., description="维修阶段：before / during / after"),
    file: UploadFile = File(..., description="图片文件（jpg/png/webp/heic）"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    # 确认维修记录存在
    repair = repair_service.get_repair(db, repair_id)
    if not repair:
        raise HTTPException(status_code=404, detail="维修记录不存在")

    unique_name, file_path = _save_file(file)

    # 添加水印（位置 + 日期）
    apply_watermark(file_path, repair.location, repair.repair_date)

    # 生成缩略图
    thumb_name = generate_thumbnail(file_path)

    photo = repair_service.add_photo(
        db,
        repair_id=repair_id,
        phase=phase,
        filename=unique_name,
        original_name=file.filename,
        filepath=file_path,
        thumb_filename=thumb_name or None,
    )
    return photo


@router.delete("/repairs/{repair_id}/photos/{photo_id}", status_code=204, summary="删除照片")
def delete_photo(repair_id: int, photo_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    ok = repair_service.delete_photo(db, photo_id)
    if not ok:
        raise HTTPException(status_code=404, detail="照片不存在")
