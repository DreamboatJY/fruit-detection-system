# =============================================================================
# 检测 API 路由模块
# =============================================================================
# 功能说明：
#   - 定义检测相关的 API 接口
#   - 处理图片上传、检测请求、结果返回
#   - 提供历史记录和目标类别查询接口
#   - 检测结果持久化存储到 PostgreSQL 数据库
#
# API 接口列表：
#   POST /api/detection/single    - 单图检测
#   GET  /api/detection/history   - 获取检测历史记录（从数据库）
#   GET  /api/detection/{id}      - 获取单个检测记录
#   DELETE /api/detection/{id}    - 删除检测记录
#   GET  /api/detection/targets/list - 获取可检测目标列表
#
# 使用示例：
#   # 前端调用
#   const formData = new FormData();
#   formData.append('file', imageFile);
#   formData.append('model_name', 'rsod-yolo11n');
#   const response = await fetch('/api/detection/single', {
#       method: 'POST',
#       body: formData
#   });
# =============================================================================

# 导入 os 模块，用于文件路径操作
import os
import time
import uuid
import csv
import io
import json
import zipfile
import base64
import binascii
from datetime import datetime
from typing import List

# 导入日志模块
import logging

# 创建 logger 实例
logger = logging.getLogger(__name__)

# 导入 FastAPI 相关组件
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Path, Response, status, BackgroundTasks
from fastapi.responses import StreamingResponse

import cv2
import numpy as np

# 导入检测服务
from app.services.detection_service import detection_service
from app.services.camera_detection_service import camera_detection_service

# 导入 MinIO 服务
from app.services.minio_service import minio_service

# 导入文件工具函数
from app.utils.file_utils import save_upload_file, ensure_directories, get_file_url

# 导入应用配置
from app.config import settings

# 导入数据模型
from app.models.schemas import (
    SingleDetectionResponse,   # 单图检测响应模型
    BatchDetectionResponse,    # 批量检测响应模型
    BatchDetectionSummary,     # 批量检测汇总模型
    BatchDetectionItem,        # 批量检测单项模型
    HistoryResponse,          # 历史记录响应模型
    TargetListResponse,       # 目标列表响应模型
    TargetItem,               # 目标项数据模型
    HistoryItem               # 历史记录项数据模型
)

# 导入数据库模型
from app.models.database import (
    User,
    BatchDetectionTask,
    DetectionRecord,
    DetectionResult as DBDetectionResult,
    SessionLocal,
)

# 导入认证依赖
from app.core.security import get_current_user

# 创建 API 路由实例
# prefix: 所有路由的前缀，如 /api/detection
# tags: 用于 OpenAPI 文档分组
router = APIRouter(prefix="/detection", tags=["detection"])

# 在模块加载时确保必要的目录存在
ensure_directories()


def _to_uuid(value):
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(str(value))


def _object_url(bucket: str, key) -> str:
    if not key:
        return ""
    return f"http://localhost:8000/api/detection/files/{bucket}/{os.path.basename(key)}"


def _record_to_batch_item(record: DetectionRecord) -> BatchDetectionItem:
    boxes = [
        {
            "x1": result.x1,
            "y1": result.y1,
            "x2": result.x2,
            "y2": result.y2,
            "confidence": result.confidence,
            "class_id": result.class_id,
            "class_name": result.class_name,
            "chinese_name": result.chinese_name,
        }
        for result in (record.results or [])
    ]
    result_data = None
    if record.status == "completed":
        from app.models.schemas import DetectionResult, DetectionBox

        result_data = DetectionResult(
            detection_id=str(record.id),
            image_url=_object_url(settings.minio.original_bucket, record.original_image_key),
            result_image_url=_object_url(settings.minio.results_bucket, record.result_image_key),
            boxes=[DetectionBox(**box) for box in boxes],
            total_objects=record.total_objects or 0,
            detection_time=round(record.detection_time or 0, 3),
            model_name=record.model_name or "rsod-yolo11n",
            created_at=record.created_at,
        )

    filename = os.path.basename(record.original_image_key) if record.original_image_key else f"{record.id}.jpg"
    return BatchDetectionItem(
        detection_id=str(record.id),
        filename=filename,
        status=record.status or "pending",
        message="检测成功" if record.status == "completed" else (record.error_message or record.status or "pending"),
        result=result_data,
        error=record.error_message,
    )


def _task_to_summary(db, task: BatchDetectionTask, include_items: bool = False) -> BatchDetectionSummary:
    processed = (task.success_count or 0) + (task.failed_count or 0)
    progress = round(processed / task.total_count * 100, 1) if task.total_count else 0
    items = []
    if include_items:
        records = (
            db.query(DetectionRecord)
            .filter(DetectionRecord.batch_id == task.id)
            .order_by(DetectionRecord.created_at.asc())
            .all()
        )
        items = [_record_to_batch_item(record) for record in records]

    return BatchDetectionSummary(
        batch_id=str(task.id),
        total=task.total_count or 0,
        completed=task.success_count or 0,
        failed=task.failed_count or 0,
        status=task.status or "pending",
        progress=progress,
        total_objects=task.total_objects or 0,
        detection_time=round(task.total_time or 0, 3),
        model_name=task.model_name or "rsod-yolo11n",
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        error_summary=task.error_summary,
        items=items,
    )


def _sync_batch_counters(db, task: BatchDetectionTask):
    records = db.query(DetectionRecord).filter(DetectionRecord.batch_id == task.id).all()
    task.success_count = sum(1 for record in records if record.status == "completed")
    task.failed_count = sum(1 for record in records if record.status == "failed")
    task.total_objects = sum(record.total_objects or 0 for record in records if record.status == "completed")
    task.total_time = sum(record.detection_time or 0 for record in records if record.status == "completed")
    errors = [record.error_message for record in records if record.error_message]
    task.error_summary = "; ".join(errors[:5]) if errors else None
    if task.status != "cancelled":
        processed = task.success_count + task.failed_count
        if processed >= task.total_count:
            task.status = "completed" if task.failed_count == 0 else ("failed" if task.success_count == 0 else "partial_failed")
            task.completed_at = task.completed_at or datetime.now()
        elif processed > 0:
            task.status = "processing"
    task.updated_at = datetime.now()
    logger.info(
        "批量任务计数同步 - batch_id=%s total=%s success=%s failed=%s status=%s",
        task.id,
        task.total_count,
        task.success_count,
        task.failed_count,
        task.status,
    )


def _clamp_float(value, default: float, minimum: float, maximum: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, number))


def _clamp_int(value, default: int, minimum: int, maximum: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, number))


def _process_batch_task(batch_id: str):
    batch_uuid = _to_uuid(batch_id)
    db = SessionLocal()
    try:
        logger.info("批量检测后台任务启动 - batch_id=%s", batch_uuid)
        task = db.query(BatchDetectionTask).filter(BatchDetectionTask.id == batch_uuid).first()
        if not task:
            logger.warning("批量检测后台任务未找到任务记录 - batch_id=%s", batch_uuid)
            return

        task.status = "processing"
        task.started_at = task.started_at or datetime.now()
        task.updated_at = datetime.now()
        db.commit()
        logger.info(
            "批量检测任务进入处理中 - batch_id=%s user_id=%s model=%s total=%s",
            task.id,
            task.user_id,
            task.model_name,
            task.total_count,
        )

        records = (
            db.query(DetectionRecord)
            .filter(DetectionRecord.batch_id == batch_uuid, DetectionRecord.status == "pending")
            .order_by(DetectionRecord.created_at.asc())
            .all()
        )
        logger.info("批量检测待处理记录数 - batch_id=%s pending=%s", batch_uuid, len(records))

        for index, record in enumerate(records, start=1):
            db.refresh(task)
            if task.status == "cancelled":
                logger.info("批量检测任务已取消，停止后台处理 - batch_id=%s processed_index=%s", batch_uuid, index)
                break

            image_path = record.original_image_key
            file_exists = bool(image_path and os.path.exists(image_path))
            logger.info(
                "批量检测单项开始 - batch_id=%s record_id=%s index=%s/%s image_path=%s exists=%s",
                batch_uuid,
                record.id,
                index,
                len(records),
                image_path,
                file_exists,
            )
            record.status = "processing"
            record.updated_at = datetime.now()
            db.commit()

            try:
                result = detection_service.detect_single_image(
                    image_path=image_path,
                    user_id=str(task.user_id) if task.user_id is not None else None,
                    model_name=task.model_name,
                    minio_svc=minio_service,
                    detection_type="batch",
                    detection_id=record.id,
                    batch_id=batch_uuid,
                )
                logger.info(
                    "批量检测单项推理完成 - batch_id=%s record_id=%s objects=%s time=%s",
                    batch_uuid,
                    record.id,
                    result.total_objects if result else None,
                    result.detection_time if result else None,
                )
            except Exception as e:
                logger.exception(
                    "批量检测后台处理失败 - batch_id=%s record_id=%s image_path=%s error=%s",
                    batch_uuid,
                    record.id,
                    image_path,
                    str(e),
                )
                record = db.query(DetectionRecord).filter(DetectionRecord.id == record.id).first()
                record.status = "failed"
                record.error_message = str(e)
                record.updated_at = datetime.now()
                db.commit()
            finally:
                db.expire_all()
                latest_record = db.query(DetectionRecord).filter(DetectionRecord.id == record.id).first()
                logger.info(
                    "批量检测单项数据库状态 - batch_id=%s record_id=%s status=%s error=%s original_key=%s result_key=%s",
                    batch_uuid,
                    latest_record.id if latest_record else record.id,
                    latest_record.status if latest_record else None,
                    latest_record.error_message if latest_record else None,
                    latest_record.original_image_key if latest_record else None,
                    latest_record.result_image_key if latest_record else None,
                )
                should_delete_temp = latest_record and latest_record.status == "completed"
                if should_delete_temp and image_path and os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                        logger.info("批量检测临时文件已删除 - batch_id=%s record_id=%s path=%s", batch_uuid, record.id, image_path)
                    except Exception:
                        logger.warning("删除临时文件失败: %s", image_path)

            db.expire_all()
            task = db.query(BatchDetectionTask).filter(BatchDetectionTask.id == batch_uuid).first()
            _sync_batch_counters(db, task)
            db.commit()

        db.expire_all()
        task = db.query(BatchDetectionTask).filter(BatchDetectionTask.id == batch_uuid).first()
        if task and task.status != "cancelled":
            _sync_batch_counters(db, task)
            db.commit()
            logger.info(
                "批量检测后台任务结束 - batch_id=%s status=%s success=%s failed=%s total=%s",
                task.id,
                task.status,
                task.success_count,
                task.failed_count,
                task.total_count,
            )
    except Exception:
        logger.exception("批量检测后台任务异常退出 - batch_id=%s", batch_uuid)
        raise
    finally:
        db.close()


# =============================================================================
# 单图检测接口
# =============================================================================

@router.post("/camera/detect")
async def detect_camera_frame(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """
    摄像头实时检测接口。

    接收前端截取的 Base64 JPEG 帧，只执行轻量推理并返回检测框，不写入历史记录。
    """
    try:
        image_data = request.get("image") if isinstance(request, dict) else None
        if not image_data:
            return {"success": False, "message": "缺少图像数据"}

        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        try:
            image_bytes = base64.b64decode(image_data, validate=True)
        except (binascii.Error, ValueError):
            return {"success": False, "message": "图像 Base64 数据无效"}

        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            return {"success": False, "message": "图像解码失败"}

        confidence_threshold = _clamp_float(
            request.get("confidence_threshold"),
            settings.confidence_threshold,
            0.0,
            1.0,
        )
        iou_threshold = _clamp_float(
            request.get("iou_threshold"),
            settings.iou_threshold,
            0.0,
            1.0,
        )
        model_image_size = _clamp_int(
            request.get("model_image_size"),
            320,
            160,
            1280,
        )

        result = camera_detection_service.detect_image(
            image,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
            model_image_size=model_image_size,
        )
        return {
            "success": True,
            "message": "检测成功",
            "data": {
                "boxes": result.get("boxes", []),
                "frame_index": result.get("frame_index", 0),
                "fps": result.get("fps", 0),
                "detection_time": round(result.get("detection_time", 0), 3),
                "total_objects": result.get("total_objects", 0),
                "confidence_threshold": confidence_threshold,
                "iou_threshold": iou_threshold,
                "model_image_size": model_image_size,
            },
        }
    except Exception as e:
        logger.exception("摄像头帧检测失败 - 用户ID: %s", current_user.id)
        return {"success": False, "message": f"图像检测失败: {str(e)}"}


@router.post("/single", response_model=SingleDetectionResponse)
async def detect_single_image(
    file: UploadFile = File(...),      # 上传的图片文件（必填）
    model_name: str = Form("rsod-yolo11n"), # 使用的模型名称（可选）
    current_user: User = Depends(get_current_user)  # 当前登录用户
):
    """
    单图目标检测接口

    功能：
    - 接收用户上传的图片
    - 保存图片到服务器
    - 调用检测服务进行目标检测
    - 保存检测记录到数据库
    - 返回检测结果

    参数：
        file: 上传的图片文件，支持 jpg、png 等格式
        model_name: 使用的模型名称（可选，默认 rsod-yolo11n）
        current_user: 当前登录用户（由 JWT 自动解析）

    返回：
        SingleDetectionResponse: 包含检测结果的响应

    响应示例：
        {
            "success": true,
            "message": "检测成功",
            "data": {
                "detection_id": "uuid-string",
                "image_url": "http://localhost:8000/static/uploads/xxx.jpg",
                "result_image_url": "http://localhost:8000/static/results/xxx.jpg",
                "boxes": [...],
                "total_objects": 5,
                "detection_time": 0.523,
                "model_name": "rsod-yolo11n",
                "created_at": "2024-12-01T14:30:00"
            }
        }
    """
    try:
        # 确保临时上传目录存在
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        # 保存上传的文件到服务器
        # save_upload_file 是异步函数，使用 await 调用
        filename = await save_upload_file(file, settings.upload_dir)

        # 构建图片的完整路径
        image_path = os.path.join(settings.upload_dir, filename)

        logger.info("开始检测图片: %s, 模型: %s, 用户ID: %s", image_path, model_name, current_user.id)

        # 调用检测服务进行单图检测（支持用户 ID）
        result = detection_service.detect_single_image(image_path, current_user.id, model_name, minio_service)

        # 检测完成后，删除临时上传的文件（节省空间）
        try:
            logger.info("删除临时文件: %s", image_path)
            os.remove(image_path)
        except:
            pass  # 删除失败不影响流程

        # 返回成功的响应
        return SingleDetectionResponse(
            success=True,                    # 请求成功
            message="检测成功",             # 提示信息
            data=result                      # 检测结果数据
        )

    except FileNotFoundError as e:
        logger.error("模型文件未找到: %s", settings.yolo_model_path)
        raise HTTPException(
            status_code=500,
            detail="模型文件未找到"
        )
    except Exception as e:
        logger.exception("单图检测失败 - 用户ID: %s, 错误: %s", current_user.id, str(e))
        raise HTTPException(
            status_code=500,                 # HTTP 状态码：服务器内部错误
            detail=f"检测失败: {str(e)}"    # 详细错误信息
        )


# =============================================================================
# 批量检测接口
# =============================================================================

@router.post("/batch", response_model=BatchDetectionResponse)
async def detect_batch_images(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    model_name: str = Form("rsod-yolo11n"),
    current_user: User = Depends(get_current_user)
):
    """
    批量目标检测接口

    功能：
    - 接收多张图片并创建批任务
    - 保存待处理记录后立即返回 batch_id
    - 后台串行执行推理，前端通过查询接口轮询进度
    """
    if not files:
        raise HTTPException(status_code=400, detail="请至少上传一张图片")

    if len(files) > settings.max_batch_images:
        raise HTTPException(status_code=400, detail=f"单次最多支持 {settings.max_batch_images} 张图片")

    batch_id = uuid.uuid4()
    os.makedirs(settings.upload_dir, exist_ok=True)

    db = SessionLocal()
    saved_paths = []
    try:
        logger.info(
            "创建批量检测任务 - batch_id=%s user_id=%s model=%s file_count=%s",
            batch_id,
            current_user.id,
            model_name,
            len(files),
        )
        task = BatchDetectionTask(
            id=batch_id,
            user_id=_to_uuid(current_user.id),
            model_name=model_name,
            total_count=len(files),
            status="pending",
        )
        db.add(task)

        total_upload_size = 0
        for file in files:
            original_filename = file.filename or "image"
            if not file.content_type or not file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail=f"{original_filename} 不是图片文件")

            content = await file.read()
            file_size = len(content)
            total_upload_size += file_size
            if file_size > settings.max_image_size_mb * 1024 * 1024:
                raise HTTPException(status_code=400, detail=f"{original_filename} 超过单图大小限制")
            if total_upload_size > settings.max_batch_upload_size_mb * 1024 * 1024:
                raise HTTPException(status_code=400, detail="超过单批总上传大小限制")

            ext = os.path.splitext(original_filename)[1] or ".jpg"
            filename = f"{uuid.uuid4().hex}{ext}"
            image_path = os.path.join(settings.upload_dir, filename)
            with open(image_path, "wb") as output:
                output.write(content)
            saved_paths.append(image_path)
            logger.info(
                "批量检测文件已保存 - batch_id=%s original_filename=%s content_type=%s size=%s path=%s",
                batch_id,
                original_filename,
                file.content_type,
                file_size,
                image_path,
            )

            db.add(DetectionRecord(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                batch_id=batch_id,
                type="batch",
                status="pending",
                model_name=model_name,
                model_version="1.0.0",
                original_image_key=image_path,
            ))

        db.commit()
        background_tasks.add_task(_process_batch_task, batch_id)
        db.refresh(task)
        logger.info("批量检测任务创建成功，已加入后台任务 - batch_id=%s", batch_id)

        return BatchDetectionResponse(
            success=True,
            message="批量检测任务已创建",
            data=_task_to_summary(db, task, include_items=True),
        )
    except HTTPException:
        db.rollback()
        for path in saved_paths:
            if os.path.exists(path):
                os.remove(path)
        raise
    except Exception as e:
        db.rollback()
        for path in saved_paths:
            if os.path.exists(path):
                os.remove(path)
        logger.exception("创建批量检测任务失败")
        raise HTTPException(status_code=500, detail=f"创建批量任务失败: {str(e)}")
    finally:
        db.close()


@router.get("/batch/{batch_id}", response_model=BatchDetectionResponse)
async def get_batch_status(
    batch_id: str = Path(..., description="批量任务 ID"),
    current_user: User = Depends(get_current_user)
):
    batch_uuid = _to_uuid(batch_id)
    db = SessionLocal()
    try:
        task = db.query(BatchDetectionTask).filter(BatchDetectionTask.id == batch_uuid).first()
        if not task:
            raise HTTPException(status_code=404, detail="批量任务不存在")
        if task.user_id != _to_uuid(current_user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该批量任务")
        _sync_batch_counters(db, task)
        db.commit()
        db.refresh(task)
        return BatchDetectionResponse(success=True, message="获取成功", data=_task_to_summary(db, task))
    finally:
        db.close()


@router.get("/batch/{batch_id}/items", response_model=BatchDetectionResponse)
async def get_batch_items(
    batch_id: str = Path(..., description="批量任务 ID"),
    current_user: User = Depends(get_current_user)
):
    batch_uuid = _to_uuid(batch_id)
    db = SessionLocal()
    try:
        task = db.query(BatchDetectionTask).filter(BatchDetectionTask.id == batch_uuid).first()
        if not task:
            raise HTTPException(status_code=404, detail="批量任务不存在")
        if task.user_id != _to_uuid(current_user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该批量任务")
        return BatchDetectionResponse(success=True, message="获取成功", data=_task_to_summary(db, task, include_items=True))
    finally:
        db.close()


@router.post("/batch/{batch_id}/retry-failed", response_model=BatchDetectionResponse)
async def retry_failed_batch_items(
    background_tasks: BackgroundTasks,
    batch_id: str = Path(..., description="批量任务 ID"),
    current_user: User = Depends(get_current_user)
):
    batch_uuid = _to_uuid(batch_id)
    db = SessionLocal()
    try:
        task = db.query(BatchDetectionTask).filter(BatchDetectionTask.id == batch_uuid).first()
        if not task:
            raise HTTPException(status_code=404, detail="批量任务不存在")
        if task.user_id != _to_uuid(current_user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该批量任务")

        failed_records = db.query(DetectionRecord).filter(
            DetectionRecord.batch_id == batch_uuid,
            DetectionRecord.status == "failed",
            DetectionRecord.original_image_key.isnot(None),
        ).all()
        retryable = [record for record in failed_records if os.path.exists(record.original_image_key)]
        if not retryable:
            raise HTTPException(status_code=400, detail="没有可重试的失败图片")

        for record in retryable:
            record.status = "pending"
            record.error_message = None
            record.updated_at = datetime.now()
        task.status = "pending"
        task.completed_at = None
        _sync_batch_counters(db, task)
        db.commit()
        background_tasks.add_task(_process_batch_task, batch_id)
        return BatchDetectionResponse(success=True, message="失败图片已重新入队", data=_task_to_summary(db, task, include_items=True))
    finally:
        db.close()


@router.post("/batch/{batch_id}/cancel", response_model=BatchDetectionResponse)
async def cancel_batch(
    batch_id: str = Path(..., description="批量任务 ID"),
    current_user: User = Depends(get_current_user)
):
    batch_uuid = _to_uuid(batch_id)
    db = SessionLocal()
    try:
        task = db.query(BatchDetectionTask).filter(BatchDetectionTask.id == batch_uuid).first()
        if not task:
            raise HTTPException(status_code=404, detail="批量任务不存在")
        if task.user_id != _to_uuid(current_user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该批量任务")
        task.status = "cancelled"
        task.completed_at = datetime.now()
        task.updated_at = datetime.now()
        db.commit()
        db.refresh(task)
        return BatchDetectionResponse(success=True, message="批量任务已取消", data=_task_to_summary(db, task, include_items=True))
    finally:
        db.close()


def _load_batch_for_export(db, batch_id: str, user_id: str) -> BatchDetectionTask:
    task = db.query(BatchDetectionTask).filter(BatchDetectionTask.id == _to_uuid(batch_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="批量任务不存在")
    if task.user_id != _to_uuid(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该批量任务")
    return task


def _batch_export_rows(records: List[DetectionRecord]) -> List[dict]:
    rows = []
    for record in records:
        filename = os.path.basename(record.original_image_key) if record.original_image_key else ""
        if record.results:
            for result in record.results:
                rows.append({
                    "filename": filename,
                    "status": record.status,
                    "total_objects": record.total_objects or 0,
                    "class_name": result.class_name,
                    "chinese_name": result.chinese_name or "",
                    "confidence": result.confidence,
                    "x1": result.x1,
                    "y1": result.y1,
                    "x2": result.x2,
                    "y2": result.y2,
                    "detection_time": round(record.detection_time or 0, 3),
                    "error_message": record.error_message or "",
                })
        else:
            rows.append({
                "filename": filename,
                "status": record.status,
                "total_objects": record.total_objects or 0,
                "class_name": "",
                "chinese_name": "",
                "confidence": "",
                "x1": "",
                "y1": "",
                "x2": "",
                "y2": "",
                "detection_time": round(record.detection_time or 0, 3),
                "error_message": record.error_message or "",
            })
    return rows


@router.get("/batch/{batch_id}/export/json")
async def export_batch_json(
    batch_id: str = Path(..., description="批量任务 ID"),
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        task = _load_batch_for_export(db, batch_id, current_user.id)
        summary = _task_to_summary(db, task, include_items=True)
        content = json.dumps(summary.dict(), ensure_ascii=False, default=str).encode("utf-8")
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="batch_{batch_id}.json"'},
        )
    finally:
        db.close()


@router.get("/batch/{batch_id}/export/csv")
async def export_batch_csv(
    batch_id: str = Path(..., description="批量任务 ID"),
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        _load_batch_for_export(db, batch_id, current_user.id)
        records = db.query(DetectionRecord).filter(DetectionRecord.batch_id == _to_uuid(batch_id)).all()
        rows = _batch_export_rows(records)
        output = io.StringIO()
        fieldnames = ["filename", "status", "total_objects", "class_name", "chinese_name", "confidence", "x1", "y1", "x2", "y2", "detection_time", "error_message"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        return Response(
            content=output.getvalue().encode("utf-8-sig"),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="batch_{batch_id}.csv"'},
        )
    finally:
        db.close()


@router.get("/batch/{batch_id}/export/zip")
async def export_batch_zip(
    batch_id: str = Path(..., description="批量任务 ID"),
    current_user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        task = _load_batch_for_export(db, batch_id, current_user.id)
        records = db.query(DetectionRecord).filter(DetectionRecord.batch_id == _to_uuid(batch_id)).all()
        rows = _batch_export_rows(records)
        summary = _task_to_summary(db, task, include_items=True)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            csv_output = io.StringIO()
            fieldnames = ["filename", "status", "total_objects", "class_name", "chinese_name", "confidence", "x1", "y1", "x2", "y2", "detection_time", "error_message"]
            writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            zf.writestr("summary.csv", csv_output.getvalue())
            zf.writestr("detections.json", json.dumps(summary.dict(), ensure_ascii=False, default=str, indent=2))

            for record in records:
                for folder, bucket, key in (
                    ("original", settings.minio.original_bucket, record.original_image_key),
                    ("results", settings.minio.results_bucket, record.result_image_key),
                ):
                    if not key:
                        continue
                    filename = os.path.basename(key)
                    try:
                        if os.path.exists(key):
                            with open(key, "rb") as local_file:
                                zf.writestr(f"{folder}/{filename}", local_file.read())
                        else:
                            response = minio_service.client.get_object(bucket, filename)
                            zf.writestr(f"{folder}/{filename}", response.read())
                            response.close()
                            response.release_conn()
                    except Exception as e:
                        logger.warning("导出文件失败: %s %s", filename, e)

        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="batch_{batch_id}.zip"'},
        )
    finally:
        db.close()


# =============================================================================
# 检测历史记录接口
# =============================================================================

@router.get("/history", response_model=HistoryResponse)
async def get_detection_history(
    page: int = 1,        # 页码（从 1 开始）
    page_size: int = 10,   # 每页记录数
    current_user: User = Depends(get_current_user)  # 当前登录用户
):
    """
    获取检测历史记录接口

    功能：
    - 从 PostgreSQL 数据库查询检测历史记录
    - 支持分页查询
    - 支持按用户 ID 筛选

    参数：
        page: 页码，默认 1
        page_size: 每页记录数，默认 10
        current_user: 当前登录用户（由 JWT 自动解析）

    返回：
        HistoryResponse: 包含历史记录列表的响应

    响应示例：
        {
            "success": true,
            "message": "获取成功",
            "data": [
                {
                    "id": "uuid-string",
                    "image_url": "http://localhost:8000/static/uploads/xxx.jpg",
                    "result_image_url": "http://localhost:8000/static/results/xxx.jpg",
                    "total_objects": 3,
                    "created_at": "2024-12-01T14:30:00",
                    "model_name": "rsod-yolo11n"
                },
                ...
            ],
            "total": 15
        }
    """
    db = None
    try:
        db = SessionLocal()
        logger.info("查询检测历史记录 - 用户ID: %s, 页码: %d, 每页条数: %d",
                     current_user.id, page, page_size)

        records = (
            db.query(DetectionRecord)
            .filter(DetectionRecord.user_id == current_user.id, DetectionRecord.batch_id.is_(None))
            .order_by(DetectionRecord.created_at.desc())
            .limit(page_size * page)
            .all()
        )
        batch_tasks = (
            db.query(BatchDetectionTask)
            .filter(BatchDetectionTask.user_id == _to_uuid(current_user.id))
            .order_by(BatchDetectionTask.created_at.desc())
            .limit(page_size * page)
            .all()
        )

        # 计算分页
        start = (page - 1) * page_size
        end = start + page_size

        # 转换为 HistoryItem 列表
        history_items = []
        combined_items = []
        for task in batch_tasks:
            first_record = (
                db.query(DetectionRecord)
                .filter(DetectionRecord.batch_id == task.id, DetectionRecord.status == "completed")
                .order_by(DetectionRecord.created_at.asc())
                .first()
            )
            image_url = _object_url(settings.minio.original_bucket, first_record.original_image_key) if first_record else ""
            result_url = _object_url(settings.minio.results_bucket, first_record.result_image_key) if first_record else ""
            combined_items.append(HistoryItem(
                id=str(task.id),
                image_url=image_url,
                result_image_url=result_url,
                total_objects=task.total_objects or 0,
                created_at=task.created_at,
                model_name=task.model_name or "rsod-yolo11n",
                filename=f"批量任务 {str(task.id)[:8]}",
                status=task.status or "pending",
                type="batch",
                time=task.created_at.strftime("%Y-%m-%d %H:%M") if task.created_at else "",
                count=task.total_count or 0,
                detected_targets=[]
            ))

        for record in records:
            # 获取文件名（从 image_key 中提取）
            # 格式：uploads/xxx.jpg 或 results/xxx.jpg
            original_filename = os.path.basename(record.original_image_key) if record.original_image_key else ""
            result_filename = os.path.basename(record.result_image_key) if record.result_image_key else ""
            
            # 构建 FastAPI 代理接口 URL
            # 格式：http://localhost:8000/api/detection/files/{bucket}/{filename}
            if original_filename:
                image_url = f"http://localhost:8000/api/detection/files/rsod-original/{original_filename}"
            else:
                image_url = ""
            
            if result_filename:
                result_url = f"http://localhost:8000/api/detection/files/rsod-results/{result_filename}"
            else:
                result_url = ""

            combined_items.append(HistoryItem(
                id=str(record.id),
                image_url=image_url,
                result_image_url=result_url,
                total_objects=record.total_objects or 0,
                created_at=record.created_at,
                model_name=record.model_name or "rsod-yolo11n",
                filename=original_filename or "detection.jpg",
                status=record.status or "completed",
                type=record.type or "single",
                time=record.created_at.strftime("%Y-%m-%d %H:%M") if record.created_at else "",
                count=1,
                detected_targets=[]  # 暂时留空
            ))

        combined_items.sort(key=lambda item: item.created_at, reverse=True)
        history_items = combined_items[start:end]

        logger.info("查询检测历史记录成功 - 用户ID: %s, 总数: %d, 返回: %d",
                     current_user.id, len(combined_items), len(history_items))

        # 返回历史记录响应
        return HistoryResponse(
            success=True,                          # 请求成功
            message="获取成功",                     # 提示信息
            data=history_items,                    # 当前页的数据
            total=len(combined_items)              # 总记录数
        )

    except Exception as e:
        logger.exception("获取检测历史记录失败 - 用户ID: %s", current_user.id)
        raise HTTPException(
            status_code=500,
            detail=f"获取历史记录失败: {str(e)}"
        )
    finally:
        try:
            db.close()
        except Exception:
            pass


# =============================================================================
# 目标类别列表接口
# =============================================================================

@router.get("/targets/list", response_model=TargetListResponse)
async def get_target_list():
    """
    获取可检测目标类别列表接口

    功能：
    - 返回系统支持检测的所有目标类别
    - NEU-DET 数据集包含 6 类钢材表面缺陷

    返回：
        TargetListResponse: 包含目标类别列表的响应
    """
    # 定义 NEU-DET 数据集支持检测的缺陷类别列表
    targets = [
        TargetItem(id=0, name="crazing", chinese_name="裂纹", description="钢材表面裂纹缺陷"),
        TargetItem(id=1, name="inclusion", chinese_name="夹杂物", description="钢材表面夹杂物缺陷"),
        TargetItem(id=2, name="patches", chinese_name="斑块", description="钢材表面斑块缺陷"),
        TargetItem(id=3, name="pitted_surface", chinese_name="麻面", description="钢材表面麻点缺陷"),
        TargetItem(id=4, name="rolled-in_scale", chinese_name="轧制氧化皮", description="轧制氧化皮缺陷"),
        TargetItem(id=5, name="scratches", chinese_name="划痕", description="钢材表面划痕缺陷"),
    ]

    # 返回目标列表响应
    return TargetListResponse(
        success=True,              # 请求成功
        message="获取成功",         # 提示信息
        data=targets              # 目标类别列表
    )


# =============================================================================
# 获取单个检测记录接口
# =============================================================================

@router.get("/detail/{detection_id}", response_model=SingleDetectionResponse)
async def get_detection_by_id(
    detection_id: str = Path(..., description="检测记录 ID"),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个检测记录接口

    功能：
    - 根据检测 ID 从数据库查询详细检测记录

    参数：
        detection_id: 检测记录 ID

    返回：
        SingleDetectionResponse: 包含检测结果的响应
    """
    try:
        # 调用检测服务获取检测记录
        record = detection_service.get_detection_by_id(detection_id)

        if not record:
            raise HTTPException(
                status_code=404,
                detail="检测记录不存在"
            )

        if record.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问该检测记录"
            )

        # 获取文件名
        original_filename = os.path.basename(record.original_image_key) if record.original_image_key else ""
        result_filename = os.path.basename(record.result_image_key) if record.result_image_key else ""
        
        # 构建 FastAPI 代理接口 URL
        if original_filename:
            image_url = f"http://localhost:8000/api/detection/files/rsod-original/{original_filename}"
        else:
            image_url = ""
        
        if result_filename:
            result_url = f"http://localhost:8000/api/detection/files/rsod-results/{result_filename}"
        else:
            result_url = ""

        # 构建响应数据
        from app.models.schemas import DetectionResult, DetectionBox

        # 查询检测结果详情
        boxes = []
        if hasattr(record, 'results') and record.results:
            for result in record.results:
                boxes.append(DetectionBox(
                    x1=result.x1,
                    y1=result.y1,
                    x2=result.x2,
                    y2=result.y2,
                    confidence=result.confidence,
                    class_id=result.class_id,
                    class_name=result.class_name,
                    chinese_name=result.chinese_name
                ))

        detection_result = DetectionResult(
            detection_id=str(record.id),
            image_url=image_url,
            result_image_url=result_url,
            boxes=boxes,
            total_objects=record.total_objects or 0,
            detection_time=record.detection_time or 0,
            model_name=record.model_name or "rsod-yolo11n",
            created_at=record.created_at
        )

        return SingleDetectionResponse(
            success=True,
            message="获取成功",
            data=detection_result
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取检测记录失败: {str(e)}"
        )


# =============================================================================
# 删除检测记录接口
# =============================================================================

@router.delete("/{detection_id}")
async def delete_detection(
    detection_id: str = Path(..., description="检测记录 ID"),
    current_user: User = Depends(get_current_user)
):
    """
    删除检测记录接口

    功能：
    - 根据检测 ID 删除数据库中的检测记录及关联数据

    参数：
        detection_id: 检测记录 ID

    返回：
        dict: 删除结果
    """
    db = None
    try:
        record = detection_service.get_detection_by_id(detection_id)
        if record:
            if record.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权删除该检测记录"
                )

            success = detection_service.delete_detection(detection_id)
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail="检测记录不存在"
                )

        else:
            try:
                batch_uuid = _to_uuid(detection_id)
            except ValueError:
                raise HTTPException(
                    status_code=404,
                    detail="检测记录不存在"
                )

            db = SessionLocal()
            task = db.query(BatchDetectionTask).filter(BatchDetectionTask.id == batch_uuid).first()
            if not task:
                raise HTTPException(
                    status_code=404,
                    detail="检测记录不存在"
                )

            if str(task.user_id) != str(current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权删除该检测记录"
                )

            success = detection_service.delete_batch_detection(batch_uuid)
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail="检测记录不存在"
                )

        return {
            "success": True,
            "message": "删除成功"
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除检测记录失败: {str(e)}"
        )
    finally:
        if db is not None:
            db.close()


# =============================================================================
# MinIO 文件代理接口
# =============================================================================

@router.get("/files/{bucket}/{filename}", response_class=Response)
def get_file(bucket: str, filename: str):
    """
    MinIO 文件代理接口

    功能：
    - 从 MinIO 获取文件并返回给前端
    - 解决前端无法直接访问 MinIO 的问题

    参数：
        bucket: MinIO Bucket 名称
        filename: 文件名

    返回：
        文件流
    """
    try:
        from app.services.minio_service import minio_service
        
        # 从 MinIO 获取文件
        response = minio_service.client.get_object(bucket, filename)
        
        # 确定内容类型
        content_type = "image/jpeg"
        if filename.endswith(".png"):
            content_type = "image/png"
        elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
            content_type = "image/jpeg"
        elif filename.endswith(".webp"):
            content_type = "image/webp"
        
        # 读取所有数据
        data = response.read()
        
        # 关闭响应对象
        response.close()
        response.release_conn()
        
        # 返回文件流
        return Response(
            content=data,
            media_type=content_type,
            headers={
                "Content-Disposition": f'inline; filename="{filename}"',
                "Content-Length": str(len(data))
            }
        )
        
    except Exception as e:
        import traceback
        logger.error("文件代理错误 - Bucket: %s, Filename: %s, 类型: %s, 信息: %s",
                     bucket, filename, type(e).__name__, str(e))
        traceback.print_exc()
        raise HTTPException(
            status_code=404,
            detail=f"文件未找到: {type(e).__name__}: {str(e)}"
        )
