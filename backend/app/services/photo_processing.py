import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

THUMB_SIZE = (300, 300)


def _get_font(size: int):
    """按优先级尝试多种字体，均失败则返回默认字体"""
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def generate_thumbnail(src_path: str) -> str:
    """生成缩略图，返回缩略图文件名（不含路径）。失败返回空字符串。"""
    base, _ = os.path.splitext(src_path)
    thumb_path = f"{base}_thumb.jpg"
    try:
        with Image.open(src_path) as img:
            img = img.convert("RGB")
            img.thumbnail(THUMB_SIZE, Image.LANCZOS)
            img.save(thumb_path, "JPEG", quality=82)
    except Exception:
        return ""
    return os.path.basename(thumb_path)


def apply_watermark(img_path: str, location: str, repair_date: str) -> None:
    """
    在图片左下角叠加三行半透明水印：
      第1行：上传时间（年月日 时:分）
      第2行：维修点位地址/区域（location 字段）
      第3行：维修点位名称（location 字段，较大字号）
    失败时静默跳过，不影响上传流程。
    """
    try:
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        lines = [
            (f"时间：{upload_time}",   20),
            (f"地点：{repair_date}",   20),
            (f"维修点位：{location}",  24),
        ]

        with Image.open(img_path) as img:
            img = img.convert("RGB")

            fonts  = [_get_font(size) for _, size in lines]
            tmp_d  = ImageDraw.Draw(img)
            pad    = 10
            gap    = 6

            # 计算每行文字尺寸
            sizes = []
            for (text, _), font in zip(lines, fonts):
                b = tmp_d.textbbox((0, 0), text, font=font)
                sizes.append((b[2] - b[0], b[3] - b[1]))

            total_h = sum(h for _, h in sizes) + gap * (len(lines) - 1)
            max_w   = max(w for w, _ in sizes)
            bw      = max_w + pad * 2
            bh      = total_h + pad * 2

            # 左下角位置
            bx = 12
            by = img.height - bh - 12

            # 半透明黑色背景
            overlay  = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ov_draw  = ImageDraw.Draw(overlay)
            ov_draw.rectangle([bx, by, bx + bw, by + bh], fill=(0, 0, 0, 150))

            merged     = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
            final_draw = ImageDraw.Draw(merged)

            # 逐行写字（颜色：前两行浅灰，第三行白色加粗）
            colors = [(200, 200, 200), (200, 200, 200), (255, 255, 255)]
            y = by + pad
            for i, ((text, _), font, (_, h), color) in enumerate(zip(lines, fonts, sizes, colors)):
                final_draw.text((bx + pad, y), text, font=font, fill=color)
                y += h + gap

            merged.save(img_path, "JPEG", quality=90)
    except Exception:
        pass
