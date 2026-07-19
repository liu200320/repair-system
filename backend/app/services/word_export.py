import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from app.models.repair import RepairRecord, PhotoPhase
from app.core.config import UPLOAD_DIR


STATUS_LABELS = {
    "pending":     "待维修",
    "in_progress": "维修中",
    "completed":   "已完成",
}

PHASE_ORDER = [
    (PhotoPhase.before, "维修前"),
    (PhotoPhase.during, "维修中"),
    (PhotoPhase.after,  "维修后"),
]


# ── 工具函数 ────────────────────────────────────────────────

def _set_cell_bg(cell, fill_hex: str):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill_hex)
    tcPr.append(shd)


def _bold_cell(cell, text: str, bg: str = "DBEAFE", align=WD_ALIGN_PARAGRAPH.CENTER):
    cell.text = text
    p = cell.paragraphs[0]
    p.alignment = align
    if p.runs:
        p.runs[0].bold = True
        p.runs[0].font.size = Pt(11)
    _set_cell_bg(cell, bg)


def _add_page_break(doc: Document):
    """在当前段落后插入分页符"""
    from docx.oxml.ns import qn as _qn
    p = doc.add_paragraph()
    run = p.add_run()
    br = OxmlElement("w:br")
    br.set(_qn("w:type"), "page")
    run._r.append(br)


def _insert_photo(cell, img_path: str, caption: str):
    """向单元格插入图片及说明文字"""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    try:
        run = p.add_run()
        run.add_picture(img_path, width=Inches(2.6))
        cap = cell.add_paragraph(caption)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.runs[0].font.size = Pt(8)
        cap.runs[0].font.color.rgb = RGBColor(0x6b, 0x72, 0x80)
    except Exception:
        p.text = "[图片加载失败]"


# ── 核心：写一条维修记录到 doc ──────────────────────────────

def _write_record(doc: Document, record: RepairRecord):
    """将单条维修记录写入已有 Document 对象"""

    # 记录标题
    title_p = doc.add_heading(
        f"维修记录  {record.record_no}  —  {record.location}", level=1
    )
    title_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if title_p.runs:
        title_p.runs[0].font.color.rgb = RGBColor(0x1a, 0x56, 0xdb)

    # ── 基本信息（3行×4列）──────────────────────────────────
    info_table = doc.add_table(rows=3, cols=4)
    info_table.style = "Table Grid"
    rows_data = [
        ("工单编号", record.record_no,   "维修日期", record.repair_date),
        ("维修点位", record.location,    "维修人员", record.repairer or "—"),
        ("当前状态", STATUS_LABELS.get(record.status.value, record.status.value), "故障描述", record.description or "—"),
    ]
    for i, (k1, v1, k2, v2) in enumerate(rows_data):
        row = info_table.rows[i]
        _bold_cell(row.cells[0], k1, align=WD_ALIGN_PARAGRAPH.LEFT)
        row.cells[1].text = str(v1)
        _bold_cell(row.cells[2], k2, align=WD_ALIGN_PARAGRAPH.LEFT)
        row.cells[3].text = str(v2)

    doc.add_paragraph()

    if record.repair_content:
        p = doc.add_paragraph()
        p.add_run("维修内容：").bold = True
        p.add_run(record.repair_content)
        doc.add_paragraph()

    # ── 照片：三行×两列（维修前/中/后 各取前两张）────────────
    doc.add_heading("维修照片", level=2)

    # 构建 6行×2列表格（每阶段：标题合并行 + 图片行）
    photo_table = doc.add_table(rows=6, cols=2)
    photo_table.style = "Table Grid"

    # 设置列宽（A4 正文宽约 15.6cm，各半）
    for row in photo_table.rows:
        for cell in row.cells:
            cell.width = Cm(7.8)

    for idx, (phase, label) in enumerate(PHASE_ORDER):
        header_row_idx = idx * 2       # 0, 2, 4
        photo_row_idx  = idx * 2 + 1  # 1, 3, 5

        # 标题行：合并两列
        hdr_row = photo_table.rows[header_row_idx]
        merged = hdr_row.cells[0].merge(hdr_row.cells[1])
        _bold_cell(merged, label, bg="DBEAFE")

        # 图片行
        phase_photos = [p for p in record.photos if p.phase == phase]
        img_row = photo_table.rows[photo_row_idx]

        for col in range(2):
            cell = img_row.cells[col]
            if col < len(phase_photos):
                photo = phase_photos[col]
                img_path = os.path.join(UPLOAD_DIR, photo.filename)
                if os.path.exists(img_path):
                    _insert_photo(cell, img_path, photo.original_name or "")
                else:
                    cell.paragraphs[0].text = "（文件不存在）"
            else:
                p = cell.paragraphs[0]
                p.text = "（无图片）"
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 页脚签字栏
    doc.add_paragraph()
    sign_p = doc.add_paragraph(f"维修人员签字：____________    日期：{record.repair_date}")
    sign_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    doc.add_paragraph("─" * 46)


# ── 对外接口 ────────────────────────────────────────────────

def export_to_word(record: RepairRecord, output_path: str) -> str:
    """导出单条维修记录"""
    doc = Document()
    _set_doc_margins(doc)

    title = doc.add_heading("维修记录报告", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if title.runs:
        title.runs[0].font.color.rgb = RGBColor(0x1a, 0x56, 0xdb)
    doc.add_paragraph()

    _write_record(doc, record)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path


def export_range_to_word(
    records: list,
    start_date: str,
    end_date: str,
    output_path: str,
) -> str:
    """将指定日期范围内的多条维修记录导出到同一个 Word 文档"""
    doc = Document()
    _set_doc_margins(doc)

    # 封面标题
    title = doc.add_heading("维修记录汇总报告", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if title.runs:
        title.runs[0].font.color.rgb = RGBColor(0x1a, 0x56, 0xdb)

    sub = doc.add_paragraph(f"导出时间范围：{start_date}  至  {end_date}    共 {len(records)} 条记录")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].font.size = Pt(12)
    doc.add_paragraph()

    for i, record in enumerate(records):
        _write_record(doc, record)
        # 记录之间插入分页符（最后一条不加）
        if i < len(records) - 1:
            _add_page_break(doc)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path


def _set_doc_margins(doc: Document):
    """设置页面边距（上下左右 2cm）"""
    from docx.oxml.ns import qn as _qn
    section = doc.sections[0]
    section.top_margin    = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin   = Cm(2)
    section.right_margin  = Cm(2)
