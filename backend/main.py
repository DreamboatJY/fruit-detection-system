from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.api.detection import router as detection_router
from app.utils.file_utils import ensure_directories
from app.api import auth
from app.db.session import engine          # 只导入 engine
from app.db.base import Base               # 正确导入 Base
from app.db.base import import_all_models

import_all_models()   # 调用该函数，导入所有模型

# 确保必要目录存在
ensure_directories()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于 YOLOv11 的钢材表面缺陷检测平台"
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# 注册路由
app.include_router(detection_router, prefix="/api")
app.include_router(auth.router)

@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.debug
    )