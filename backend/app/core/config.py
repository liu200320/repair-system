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
