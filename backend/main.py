import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1 import repair, upload, export, auth, location, stats, monitor_point
from app.core.database import engine, SessionLocal
from app.core.config import UPLOAD_DIR
import app.models.repair       # noqa
import app.models.user         # noqa
import app.models.location     # noqa
import app.models.monitor_point  # noqa  不自动建表，表由外部维护

# 自动建表
app.models.repair.Base.metadata.create_all(bind=engine)
app.models.user.Base.metadata.create_all(bind=engine)
app.models.location.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="维修记录系统 API",
    version="2.0.0",
    description="维修记录 CRUD、图片上传、Word导出、认证、统计",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(auth.router,     prefix="/api/v1", tags=["认证"])
app.include_router(repair.router,   prefix="/api/v1", tags=["维修记录"])
app.include_router(upload.router,   prefix="/api/v1", tags=["照片上传"])
app.include_router(export.router,   prefix="/api/v1", tags=["Word导出"])
app.include_router(location.router,      prefix="/api/v1", tags=["点位管理"])
app.include_router(monitor_point.router, prefix="/api/v1", tags=["监控点位"])
app.include_router(stats.router,         prefix="/api/v1", tags=["统计"])


@app.on_event("startup")
def _on_startup():
    # 1. 创建默认管理员
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

    # 2. 为已有表补充新列（向后兼容）
    try:
        with engine.connect() as conn:
            conn.execute(
                __import__("sqlalchemy").text(
                    "ALTER TABLE repair_photos ADD COLUMN thumb_filename VARCHAR(255) NULL"
                )
            )
            conn.commit()
    except Exception:
        pass  # 列已存在时忽略


@app.get("/health", tags=["健康检查"])
def health():
    return {"status": "ok", "version": "2.0.0"}
