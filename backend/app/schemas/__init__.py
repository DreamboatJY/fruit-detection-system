"""schemas 包的统一导出模块，汇总所有 Pydantic 模型供外部使用。"""

from app.schemas.detection_schema import DetectionBox, DetectionResult, SingleDetectionResponse, TargetItem, TargetListResponse
from app.schemas.detection_record_schema import DetectionRecordCreate, DetectionRecordRead, DetectionRecordUpdate
from app.schemas.detection_result_schema import DetectionResultCreate, DetectionResultRead, DetectionResultUpdate
from app.schemas.model_version_schema import ModelVersionCreate, ModelVersionRead, ModelVersionUpdate
from app.schemas.target_category_schema import TargetCategoryCreate, TargetCategoryRead, TargetCategoryUpdate
from app.schemas.user_schema import UserCreate, UserRead, UserUpdate

__all__ = [
    "DetectionBox",
    "DetectionRecordCreate",
    "DetectionRecordRead",
    "DetectionRecordUpdate",
    "DetectionResult",
    "DetectionResultCreate",
    "DetectionResultRead",
    "DetectionResultUpdate",
    "ModelVersionCreate",
    "ModelVersionRead",
    "ModelVersionUpdate",
    "SingleDetectionResponse",
    "TargetItem",
    "TargetCategoryCreate",
    "TargetCategoryRead",
    "TargetCategoryUpdate",
    "TargetListResponse",
    "UserCreate",
    "UserRead",
    "UserUpdate",
]
