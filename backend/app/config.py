import os
from pydantic import BaseModel

class Settings(BaseModel):
    """应用配置类"""
    
    # 应用基本信息
    app_name: str = os.getenv("APP_NAME", "Steel Defect Detection System")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    debug: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 目录配置
    STATIC_DIR: str = "static"
    UPLOAD_DIR: str = "static/uploads"
    RESULT_DIR: str = "static/results"
    
    # PostgreSQL配置
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_user: str = os.getenv("DB_USER", "rsod_user")
    db_password: str = os.getenv("DB_PASSWORD", "rsod_password")
    db_name: str = os.getenv("DB_NAME", "rsod_db")
    
    # Redis配置
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    
    # MinIO配置
    minio_endpoint: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    minio_bucket: str = os.getenv("MINIO_BUCKET", "rsod-bucket")
    minio_secure: bool = os.getenv("MINIO_SECURE", "false").lower() in ("true", "1", "yes")
    
    # YOLO模型配置
    YOLO_MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH", "yolo11n.pt")
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
    IOU_THRESHOLD: float = float(os.getenv("IOU_THRESHOLD", "0.45"))
    
    # 文件存储配置
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    result_dir: str = os.getenv("RESULT_DIR", "results")
    
    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

# 实例化配置对象
settings = Settings()