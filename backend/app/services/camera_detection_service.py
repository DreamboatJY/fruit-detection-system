import threading
import time
from typing import Any, Dict

import numpy as np

from app.services.detection_service import detection_service


class CameraDetectionService:
    """Lightweight per-frame detection for browser camera streams."""

    def __init__(self):
        self._lock = threading.Lock()
        self._request_semaphore = threading.Semaphore(2)
        self._frame_count = 0
        self._fps_frame_count = 0
        self._last_fps_time = time.time()
        self._last_fps = 0.0

    def detect_image(
        self,
        image: np.ndarray,
        confidence_threshold: float,
        iou_threshold: float,
        model_image_size: int,
    ) -> Dict[str, Any]:
        if detection_service.model is None:
            raise RuntimeError("模型未加载")

        with self._request_semaphore:
            start_time = time.time()
            results = detection_service.model.predict(
                source=image,
                conf=confidence_threshold,
                iou=iou_threshold,
                save=False,
                imgsz=model_image_size,
                half=False,
                verbose=False,
                stream=False,
            )

            boxes = []
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = detection_service.class_names.get(class_id, f"class_{class_id}")
                    boxes.append(
                        {
                            "x1": x1,
                            "y1": y1,
                            "x2": x2,
                            "y2": y2,
                            "confidence": confidence,
                            "class_id": class_id,
                            "class_name": class_name,
                            "chinese_name": detection_service.get_class_chinese_name(class_name),
                        }
                    )

            detection_time = time.time() - start_time
            frame_index, fps = self._update_stats()

            return {
                "boxes": boxes,
                "frame_index": frame_index,
                "fps": fps,
                "detection_time": detection_time,
                "total_objects": len(boxes),
            }

    def _update_stats(self) -> tuple[int, float]:
        with self._lock:
            self._frame_count += 1
            self._fps_frame_count += 1
            now = time.time()
            elapsed = now - self._last_fps_time
            if elapsed >= 1.0:
                self._last_fps = self._fps_frame_count / elapsed
                self._fps_frame_count = 0
                self._last_fps_time = now
            return self._frame_count, self._last_fps


camera_detection_service = CameraDetectionService()
