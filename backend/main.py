import asyncio
import glob
import os
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect as sa_inspect

from app.api.v1 import auth, consumable, export, location, monitor_point, repair, stats, upload
from app.core.config import ALLOWED_ORIGINS, EXPORT_RETENTION_DAYS, UPLOAD_DIR
from app.core.database import engine, SessionLocal
import app.models.consumable   # noqa
import app.models.location     # noqa
import app.models.monitor_point  # noqa
import app.models.repair       # noqa
import app.models.user         # noqa

# 自动建表（新部署时建表；Alembic 负责后续 schema 迁移）
app.models.repair.Base.metadata.create_all(bind=engine)
app.models.user.Base.metadata.create_all(bind=engine)
app.models.location.Base.metadata.create_all(bind=engine)
app.models.consumable.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="维修记录系统 API",
    version="2.0.0",
    description="维修记录 CRUD、图片上传、Word导出、认证、统计",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(auth.router,          prefix="/api/v1", tags=["认证"])
app.include_router(repair.router,        prefix="/api/v1", tags=["维修记录"])
app.include_router(upload.router,        prefix="/api/v1", tags=["照片上传"])
app.include_router(export.router,        prefix="/api/v1", tags=["Word导出"])
app.include_router(location.router,      prefix="/api/v1", tags=["点位管理"])
app.include_router(monitor_point.router, prefix="/api/v1", tags=["监控点位"])
app.include_router(stats.router,         prefix="/api/v1", tags=["统计"])
app.include_router(consumable.router,    prefix="/api/v1", tags=["耗材管理"])


# ── 导出文件清理 ───────────────────────────────────────────────

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
    """每24小时清理一次过期导出文件"""
    while True:
        await asyncio.sleep(24 * 3600)
        _cleanup_old_exports()


# ── Alembic 迁移 ────────────────────────────────────────────────

def _run_alembic_migrations():
    from alembic.config import Config as AlembicConfig
    from alembic import command as alembic_command

    alembic_cfg = AlembicConfig("alembic.ini")
    inspector = sa_inspect(engine)

    if not inspector.has_table("alembic_version"):
        if inspector.has_table("users"):
            # 已有旧版本数据库（无 Alembic 历史），标记到基线，再执行新迁移
            alembic_command.stamp(alembic_cfg, "001")
        else:
            # 全新部署，create_all 已建好所有表，直接标记到最新
            alembic_command.stamp(alembic_cfg, "head")

    alembic_command.upgrade(alembic_cfg, "head")


# ── 启动事件 ────────────────────────────────────────────────────

@app.on_event("startup")
async def _on_startup():
    # 1. 先执行 Alembic 迁移（必须在任何 ORM 查询前，以确保表结构最新）
    _run_alembic_migrations()

    # 2. 创建默认管理员
    from app.models.user import User
    from app.core.security import hash_password
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add(User(username="admin", hashed_pw=hash_password("admin123"),
                        full_name="管理员", role="admin"))
            db.commit()
            print("[OK] Default admin created: admin / admin123")
    finally:
        db.close()

    # 3. 启动时清理一次过期导出文件
    _cleanup_old_exports()

    # 4. 后台定时清理任务
    asyncio.create_task(_cleanup_exports_daily())


@app.get("/health", tags=["健康检查"])
def health():
    return {"status": "ok", "version": "2.0.0"}
