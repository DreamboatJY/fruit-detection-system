import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.detection_service import detection_service
from app.services.video_detection_service import video_detection_service
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
        TargetItem(id=0, name="crazing", chinese_name="裂纹", description="表面开裂缺陷"),
        TargetItem(id=1, name="inclusion", chinese_name="划痕", description="线性刮伤缺陷"),
        TargetItem(id=2, name="patches", chinese_name="斑块", description="块状瑕疵缺陷"),
        TargetItem(id=3, name="pitted_surface", chinese_name="麻点", description="密集小坑缺陷"),
        TargetItem(id=4, name="rolled-in_scale", chinese_name="压入", description="氧化皮压入缺陷"),
        TargetItem(id=5, name="scratches", chinese_name="氧化皮", description="氧化层剥落缺陷"),
    ]
    return TargetListResponse(
        success=True,
        message="获取成功",
        data=targets
    )
@router.post("/batch")
async def detect_batch_images(
    files: list[UploadFile] = File(...),
    model_name: str = Form("pest-v1")
):
    """批量图片检测接口"""
    try:
        results = []

        for file in files:
            filename = await save_upload_file(file, settings.UPLOAD_DIR)
            image_path = os.path.join(settings.UPLOAD_DIR, filename)

            result = detection_service.detect_single_image(image_path, model_name)

            results.append({
                "filename": file.filename,
                "success": True,
                "data": result
            })

        return {
            "success": True,
            "message": f"批量检测成功，共处理 {len(results)} 张图片",
            "data": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量检测失败: {str(e)}")


@router.post("/video")
async def detect_video(
    file: UploadFile = File(...),
    model_name: str = Form("pest-v1")
):
    """视频检测接口"""
    try:
        # 保存上传的视频文件
        filename = await save_upload_file(file, settings.UPLOAD_DIR)
        video_path = os.path.join(settings.UPLOAD_DIR, filename)

        # 执行视频检测
        result = video_detection_service.detect_video(video_path, model_name)

        return {
            "success": True,
            "message": "视频检测成功",
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"视频检测失败: {str(e)}")