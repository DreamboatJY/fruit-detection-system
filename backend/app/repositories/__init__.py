"""
数据仓库层统一导出模块

集中导出所有 Repository 类，方便上层模块通过统一入口引入。
"""

from app.repositories.detection_record_repository import DetectionRecordRepository
from app.repositories.detection_result_repository import DetectionResultRepository
from app.repositories.model_version_repository import ModelVersionRepository
from app.repositories.target_category_repository import TargetCategoryRepository
from app.repositories.user_repository import UserRepository

__all__ = [
    "DetectionRecordRepository",
    "DetectionResultRepository",
    "ModelVersionRepository",
    "TargetCategoryRepository",
    "UserRepository",
]
