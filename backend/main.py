import asyncio
import glob
import os
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

from app.api.v1 import access_inspection, auth, consumable, export, location, monitor_point, network_inspection, repair, stats, upload
from app.core.config import ALLOWED_ORIGINS, EXPORT_RETENTION_DAYS, UPLOAD_DIR
from app.core.database import engine, SessionLocal, Base
import app.models.access_inspection   # noqa
import app.models.access_location      # noqa
import app.models.consumable           # noqa
import app.models.location             # noqa
import app.models.monitor_point        # noqa
import app.models.network_inspection   # noqa
import app.models.network_location     # noqa
import app.models.repair               # noqa
import app.models.user                 # noqa

# 自动建表（create_all 会跳过已存在的表）
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="维修记录系统 API",
    version="2.0.0",
    description="维修记录 CRUD、图片上传、Word导出、认证、统计",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(auth.router,               prefix="/api/v1", tags=["认证"])
app.include_router(repair.router,             prefix="/api/v1", tags=["维修记录"])
app.include_router(upload.router,             prefix="/api/v1", tags=["照片上传"])
app.include_router(export.router,             prefix="/api/v1", tags=["Word导出"])
app.include_router(location.router,           prefix="/api/v1", tags=["点位管理"])
app.include_router(monitor_point.router,      prefix="/api/v1", tags=["监控点位"])
app.include_router(stats.router,              prefix="/api/v1", tags=["统计"])
app.include_router(consumable.router,         prefix="/api/v1", tags=["耗材管理"])
app.include_router(network_inspection.router, prefix="/api/v1", tags=["网络基础设施巡检"])
app.include_router(access_inspection.router,  prefix="/api/v1", tags=["门禁巡检"])


# ── 导出文件清理 ─────────────────────────────────────────────────

def _cleanup_old_exports():
    export_dir = os.path.join(UPLOAD_DIR, "exports")
    if not os.path.exists(export_dir):
        return
    cutoff = (datetime.now() - timedelta(days=EXPORT_RETENTION_DAYS)).timestamp()
    for f in glob.glob(os.path.join(export_dir, "*.docx")):
        if os.path.getmtime(f) < cutoff:
            try:
                os.remove(f)
                print(f"[cleanup] 已删除过期导出文件: {f}")
            except OSError:
                pass


async def _cleanup_exports_daily():
    while True:
        await asyncio.sleep(24 * 3600)
        _cleanup_old_exports()


# ── 启动时结构补丁（直接 SQL，避免 async 事件循环中调用 Alembic API） ──
# Alembic 命令行仍可用于 CI/部署：cd backend && alembic upgrade head

_NETWORK_LOCATIONS_SEED = [
    "鸿翼楼二楼楼梯口", "实训楼二楼楼梯口", "嘉锐楼三楼楼梯口",
    "绍年院网络机柜",   "文清楼网络机柜",   "文兴楼网络机柜",
    "众创空间",         "体育工作部",       "冻精站1楼房间",
    "蚕桑礼堂弱电间",   "团委二楼",         "牧歌院二栋",
    "综合楼四楼弱电间", "综合楼五楼弱电间", "学生服务中心二楼网络机柜",
    "实训中心办公楼",   "五谷苑5栋",        "三实牧院",
    "种畜场招待所楼梯间", "种畜场原医务室", "种畜场办公楼",
]

_ACCESS_LOCATIONS_SEED = [
    "学校大门口",
    "冻精站大门口",
    "种畜推广中心大门口",
]


def _run_startup_migrations():
    from sqlalchemy import text, inspect as sa_inspect
    inspector = sa_inspect(engine)

    with engine.begin() as conn:
        # 给旧库补 token_version 列
        if inspector.has_table("users"):
            cols = [c["name"] for c in inspector.get_columns("users")]
            if "token_version" not in cols:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN token_version INT NOT NULL DEFAULT 0"
                ))

        # 补 network_locations 种子数据（21个网络巡检地点）
        if inspector.has_table("network_locations"):
            count = conn.execute(text("SELECT COUNT(*) FROM network_locations")).scalar()
            if count == 0:
                conn.execute(
                    text("INSERT INTO network_locations (name) VALUES (:name)"),
                    [{"name": loc} for loc in _NETWORK_LOCATIONS_SEED],
                )

        # 补 access_locations 种子数据（3个门禁地点）
        if inspector.has_table("access_locations"):
            count = conn.execute(text("SELECT COUNT(*) FROM access_locations")).scalar()
            if count == 0:
                conn.execute(
                    text("INSERT INTO access_locations (name) VALUES (:name)"),
                    [{"name": loc} for loc in _ACCESS_LOCATIONS_SEED],
                )


# ── 启动事件 ─────────────────────────────────────────────────────

@app.on_event("startup")
async def _on_startup():
    # 1. 结构补丁（添加缺少的列和种子数据）
    _run_startup_migrations()

    # 2. 创建默认管理员（密码必须从环境变量获取）
    from app.models.user import User
    from app.core.security import hash_password
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            init_pw = os.getenv("ADMIN_INIT_PASSWORD")
            if not init_pw:
                raise RuntimeError(
                    "首次启动需设置环境变量 ADMIN_INIT_PASSWORD，"
                    "例如：ADMIN_INIT_PASSWORD=$(python -c \"import secrets; print(secrets.token_urlsafe(16))\")"
                )
            db.add(User(username="admin", hashed_pw=hash_password(init_pw),
                        full_name="管理员", role="admin"))
            db.commit()
            print("[OK] Default admin created: admin / <ADMIN_INIT_PASSWORD>")
    finally:
        db.close()

    # 3. 启动时清理一次过期导出文件
    _cleanup_old_exports()

    # 4. 后台定时清理任务
    asyncio.create_task(_cleanup_exports_daily())


@app.get("/health", tags=["健康检查"])
def health():
    return {"status": "ok"}
