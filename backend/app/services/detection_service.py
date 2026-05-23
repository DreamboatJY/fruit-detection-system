import os
import time
import uuid
from datetime import datetime
import cv2
from app.config import settings
from app.models.schemas import DetectionBox, DetectionResult
from app.utils.file_utils import get_file_url


class DetectionService:
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
                print(f"模型加载成功: {model_path}")
            except Exception as e:
                print(f"模型加载失败: {e}")
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
    def detect_single_image(self, image_path: str, model_name: str = "pest-v1") -> DetectionResult:
        """执行单图检测"""
        start_time = time.time()
        detection_id = str(uuid.uuid4())

        # 如果没有模型，返回模拟数据
        if self.model is None:
            return self._get_mock_result(detection_id, image_path, model_name, start_time)

        # 真实检测
        from ultralytics import YOLO
        results = self.model.predict(
            source=image_path,
            conf=settings.CONFIDENCE_THRESHOLD,
            iou=settings.IOU_THRESHOLD,
            save=False
        )

        boxes = []
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = self.class_names.get(class_id, f"class_{class_id}")
                    
                    boxes.append(DetectionBox(
                        x1=x1, y1=y1, x2=x2, y2=y2,
                        confidence=confidence, class_id=class_id, class_name=class_name
                    ))

        # 保存标注图片
        result_filename = f"result_{uuid.uuid4().hex}.jpg"
        result_path = os.path.join(settings.RESULT_DIR, result_filename)
        
        annotated_image = results[0].plot()
        cv2.imwrite(result_path, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))

        detection_time = time.time() - start_time
        image_filename = os.path.basename(image_path)

        return DetectionResult(
            detection_id=detection_id,
            image_url=get_file_url(image_filename, "uploads"),
            result_image_url=get_file_url(result_filename, "results"),
            boxes=boxes,
            total_objects=len(boxes),
            detection_time=round(detection_time, 3),
            model_name=model_name,
            created_at=datetime.now()
        )

    def _get_mock_result(self, detection_id: str, image_path: str, model_name: str, start_time: float) -> DetectionResult:
        """模拟检测结果（当模型不存在时）"""
        detection_time = time.time() - start_time
        image_filename = os.path.basename(image_path)
        
        # 模拟一些检测框
        mock_boxes = [
            DetectionBox(x1=100, y1=150, x2=300, y2=350, confidence=0.92, class_id=4, class_name="airplane"),
            DetectionBox(x1=400, y1=200, x2=550, y2=380, confidence=0.87, class_id=4, class_name="airplane"),
        ]
        
        return DetectionResult(
            detection_id=detection_id,
            image_url=get_file_url(image_filename, "uploads"),
            result_image_url=get_file_url(image_filename, "uploads"),
            boxes=mock_boxes,
            total_objects=len(mock_boxes),
            detection_time=round(detection_time, 3),
            model_name=model_name,
            created_at=datetime.now()
        )


detection_service = DetectionService()