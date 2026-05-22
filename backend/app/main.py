from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import detection
from app.api import websocket
from app.config import settings

# 创建 FastAPI 应用实例
app = FastAPI(
    title="遥感目标智能检测平台",
    description="基于YOLO的遥感图像目标检测系统API，支持飞机、油罐、立交桥、操场等目标检测",
    version="1.0.0"
)

# 配置 CORS 跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(detection.router)
app.include_router(websocket.router)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# 健康检查接口
@app.get("/health", tags=["健康检查"])
async def health_check():
    return {
        "status": "healthy",
        "service": "rsod-web-platform",
        "version": "1.0.0"
    }

# 根路径接口
@app.get("/", tags=["根路径"])
async def root():
    return {"message": "欢迎使用遥感目标智能检测平台"}

# 应用启动入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)