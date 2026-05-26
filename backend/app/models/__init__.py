"""
ORM 模型包

导出所有 SQLAlchemy ORM 模型，方便其他模块统一导入。
"""
from app.models.detection_record_model import DetectionRecord
from app.models.detection_result_model import DetectionResult
from app.models.model_version_model import ModelVersion
from app.models.target_category_model import TargetCategory
from app.models.user_model import User

__all__ = [
    "User",
    "ModelVersion",
    "DetectionRecord",
    "DetectionResult",
    "TargetCategory",
]
