import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "repair_db")

DATABASE_URL = (
    f"mysql+pymysql://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4"
)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 默认 10MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "heic"}

# CORS 允许来源，多个用逗号分隔，如 http://192.168.1.100,http://localhost:5173
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()]

EXPORT_RETENTION_DAYS = int(os.getenv("EXPORT_RETENTION_DAYS", "7"))
