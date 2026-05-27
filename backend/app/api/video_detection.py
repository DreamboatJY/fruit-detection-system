import logging

import cv2
import numpy as np
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.security import get_current_user
from app.models.database import User
from app.models.schemas import RealtimeDetectionResponse
from app.services.detection_service import detection_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/video-detection", tags=["video-detection"])


@router.post("/realtime-frame", response_model=RealtimeDetectionResponse)
async def detect_realtime_frame(
    file: UploadFile = File(...),
    model_name: str = Form("neu-det-yolo11n"),
    confidence_threshold: float = Form(0.25),
    iou_threshold: float = Form(0.7),
    current_user: User = Depends(get_current_user),
):
    """
    检测视频播放过程中的单帧图片。

    该接口仅用于实时展示，不写入历史记录，不上传 MinIO。
    """
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="上传帧为空")

        image_array = np.frombuffer(contents, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(status_code=400, detail="无法解析视频帧图片")

        result = detection_service.detect_frame_realtime(
            image=image,
            model_name=model_name,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
        )
        return RealtimeDetectionResponse(
            success=True,
            message="检测成功",
            data=result,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("视频实时帧检测失败 - 用户ID: %s", current_user.id)
        raise HTTPException(status_code=500, detail=f"实时帧检测失败: {str(e)}")
