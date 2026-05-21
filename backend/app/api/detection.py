import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.detection_service import detection_service
from app.utils.file_utils import save_upload_file, ensure_directories
from app.config import settings
from app.models.schemas import SingleDetectionResponse, TargetListResponse, TargetItem

router = APIRouter(prefix="/detection", tags=["detection"])

# 确保目录存在
ensure_directories()


@router.post("/single", response_model=SingleDetectionResponse)
async def detect_single_image(
    file: UploadFile = File(...),
    model_name: str = Form("pest-v1")
):
    """单图检测接口"""
    try:
        # 保存上传的文件
        filename = await save_upload_file(file, settings.UPLOAD_DIR)
        image_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # 执行检测
        result = detection_service.detect_single_image(image_path, model_name)
        
        return SingleDetectionResponse(
            success=True,
            message="检测成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")


@router.get("/targets/list", response_model=TargetListResponse)
async def get_target_list():
    """获取目标列表"""
    targets = [
        TargetItem(id=0, name="airplane", chinese_name="飞机", description="固定翼飞机、直升机等"),
        TargetItem(id=4, name="ship", chinese_name="船舶", description="各类船舶"),
        TargetItem(id=5, name="bus", chinese_name="公交车", description="城市公交车"),
        TargetItem(id=7, name="truck", chinese_name="卡车", description="大型货运卡车"),
    ]
    return TargetListResponse(
        success=True,
        message="获取成功",
        data=targets
    )