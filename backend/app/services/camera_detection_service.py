import os
import base64
import time
import uuid
import cv2
import numpy as np
from app.config import settings
from app.schemas.detection_schema import DetectionBox


class CameraDetectionService:
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
                print(f"摄像头检测模型加载成功: {model_path}")
            except Exception as e:
                print(f"摄像头检测模型加载失败: {e}")
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

    def detect_frame(self, frame_data: str) -> dict:
        """
        检测单帧图像
        :param frame_data: base64编码的图像数据
        :return: 检测结果字典
        """
        start_time = time.time()

        try:
            # 解码base64图像
            image_bytes = base64.b64decode(frame_data)
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if frame is None:
                return {"success": False, "error": "图像解码失败"}

            # 如果没有模型，返回模拟数据
            if self.model is None:
                return self._get_mock_result(frame, start_time)

            # 真实检测
            results = self.model.predict(
                source=frame,
                conf=settings.CONFIDENCE_THRESHOLD,
                iou=settings.IOU_THRESHOLD,
                save=False,
                verbose=False
            )

            boxes = []
            if results and results[0].boxes is not None:
                for box in results[0].boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = self.class_names.get(class_id, f"class_{class_id}")

                    boxes.append({
                        "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                        "confidence": confidence,
                        "class_id": class_id,
                        "class_name": class_name
                    })

            # 生成标注图像
            annotated_frame = results[0].plot()
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            annotated_base64 = base64.b64encode(buffer).decode('utf-8')

            detection_time = time.time() - start_time

            return {
                "success": True,
                "boxes": boxes,
                "total_objects": len(boxes),
                "detection_time": round(detection_time, 3),
                "annotated_frame": annotated_base64
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_mock_result(self, frame, start_time: float) -> dict:
        """模拟检测结果"""
        h, w = frame.shape[:2]
        mock_boxes = [
            {"x1": w * 0.1, "y1": h * 0.15, "x2": w * 0.3, "y2": h * 0.35,
            "confidence": 0.92, "class_id": 0, "class_name": "crazing"},
            {"x1": w * 0.4, "y1": h * 0.2, "x2": w * 0.55, "y2": h * 0.38,
            "confidence": 0.87, "class_id": 1, "class_name": "inclusion"},
        ]

        _, buffer = cv2.imencode('.jpg', frame)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')

        detection_time = time.time() - start_time

        return {
            "success": True,
            "boxes": mock_boxes,
            "total_objects": len(mock_boxes),
            "detection_time": round(detection_time, 3),
            "annotated_frame": annotated_base64
        }


camera_detection_service = CameraDetectionService()
