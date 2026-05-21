import os
import uuid
import shutil
from fastapi import UploadFile
from app.config import settings


async def save_upload_file(file: UploadFile, upload_dir: str) -> str:
    """保存上传的文件"""
    os.makedirs(upload_dir, exist_ok=True)
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return unique_filename


def get_file_url(filename: str, subdir: str) -> str:
    """获取文件访问URL"""
    return f"/static/{subdir}/{filename}"


def ensure_directories():
    """确保必要的目录存在"""
    os.makedirs(settings.STATIC_DIR, exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.RESULT_DIR, exist_ok=True)