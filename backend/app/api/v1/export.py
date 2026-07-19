import os
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.services import repair_service
from app.services.word_export import export_to_word, export_range_to_word

router = APIRouter()


@router.post("/repairs/{repair_id}/export", summary="导出单条维修记录为 Word")
def export_single(repair_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    record = repair_service.get_repair(db, repair_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    out_dir = os.path.join("uploads", "exports")
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, f"维修记录_{record.record_no}.docx")

    try:
        export_to_word(record, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败：{str(e)}")

    return FileResponse(
        path=output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"维修记录_{record.record_no}.docx",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''维修记录_{record.record_no}.docx"},
    )


@router.get(
    "/repairs/export/range",
    summary="按日期范围批量导出维修记录为 Word",
    description="将指定日期段内所有维修记录导出到一个 Word 文档，每条记录单独一页",
)
def export_range(
    start_date: str = Query(..., examples=["2026-07-01"], description="开始日期 YYYY-MM-DD"),
    end_date:   str = Query(..., examples=["2026-07-31"], description="结束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    # 查询日期范围内所有记录（按日期升序）
    _, records = repair_service.list_repairs(
        db,
        page=1,
        page_size=500,          # 最多 500 条，够用
        repair_date=None,
    )
    # 在 Python 层过滤日期范围（字符串比较，格式统一为 YYYY-MM-DD）
    records = [r for r in records if start_date <= r.repair_date <= end_date]
    # 按日期升序排列
    records.sort(key=lambda r: r.repair_date)

    if not records:
        raise HTTPException(status_code=404, detail=f"{start_date} 至 {end_date} 没有维修记录")

    out_dir = os.path.join("uploads", "exports")
    os.makedirs(out_dir, exist_ok=True)
    filename = f"维修汇总_{start_date}_至_{end_date}.docx"
    output_path = os.path.join(out_dir, filename)

    try:
        export_range_to_word(records, start_date, end_date, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败：{str(e)}")

    return FileResponse(
        path=output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )
