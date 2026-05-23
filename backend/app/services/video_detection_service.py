import os
import time
import uuid
import cv2
from datetime import datetime
from app.config import settings
from app.utils.file_utils import get_file_url


class VideoDetectionService:
    def __init__(self):
        self.model = None
        self.class_names = {}
        self._load_model()
        self._init_class_names()

    def _load_model(self):
        """加载YOLO模型"""
        model_path = settings.YOLO_MODEL_PATH
        if os.path.exists(model_path):
            try:
                from ultralytics import YOLO
                self.model = YOLO(model_path)
                print(f"视频检测模型加载成功: {model_path}")
            except Exception as e:
                print(f"视频检测模型加载失败: {e}")
                self.model = None
        else:
            print(f"警告: 模型文件不存在 {model_path}，将使用模拟模式")
            self.model = None

    def _init_class_names(self):
        """初始化类别名称"""
        self.class_names = {
            0: "crazing",
            1: "inclusion",
            2: "patches",
            3: "pitted_surface",
            4: "rolled-in_scale",
            5: "scratches"
        }

    def detect_video(self, video_path: str, model_name: str = "pest-v1", progress_callback=None):
        """执行视频检测，返回标注后的视频路径和检测统计"""
        start_time = time.time()
        video_id = str(uuid.uuid4())

        # 打开视频文件
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("无法打开视频文件")

        # 获取视频信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # 生成输出视频文件名
        result_filename = f"result_{video_id}.mp4"
        result_path = os.path.join(settings.RESULT_DIR, result_filename)

        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(result_path, fourcc, fps, (width, height))

        total_objects = 0
        frame_count = 0
        detection_stats = {}

        # 逐帧处理
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # 执行检测
            if self.model is not None:
                results = self.model.predict(
                    source=frame,
                    conf=settings.CONFIDENCE_THRESHOLD,
                    iou=settings.IOU_THRESHOLD,
                    verbose=False
                )

                # 绘制标注框
                annotated_frame = results[0].plot()

                # 统计当前帧目标
                frame_objects = 0
                if results[0].boxes is not None:
                    for box in results[0].boxes:
                        class_id = int(box.cls[0])
                        class_name = self.class_names.get(class_id, f"class_{class_id}")
                        detection_stats[class_name] = detection_stats.get(class_name, 0) + 1
                        frame_objects += 1

                total_objects += frame_objects
            else:
                # 模拟模式：直接复制原帧
                annotated_frame = frame.copy()

            # 写入标注帧
            out.write(annotated_frame)

            # 回调进度
            if progress_callback:
                progress = (frame_count / total_frames) * 100
                progress_callback(progress, frame_count, total_frames)

        # 释放资源
        cap.release()
        out.release()

        detection_time = time.time() - start_time
        video_filename = os.path.basename(video_path)

        return {
            "video_id": video_id,
            "original_video_url": get_file_url(video_filename, "uploads"),
            "result_video_url": get_file_url(result_filename, "results"),
            "total_frames": frame_count,
            "total_objects": total_objects,
            "detection_time": round(detection_time, 3),
            "model_name": model_name,
            "fps": fps,
            "width": width,
            "height": height,
            "detection_stats": detection_stats,
            "created_at": datetime.now().isoformat()
        }


video_detection_service = VideoDetectionService()
