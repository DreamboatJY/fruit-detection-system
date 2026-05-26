"""
检测结果数据仓库模块

提供 DetectionResult 模型特有的数据库查询方法，
包括按检测记录查询和按缺陷类别查询。
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.detection_result_model import DetectionResult
from app.repositories.base_repository import BaseRepository
from app.schemas.detection_result_schema import DetectionResultCreate, DetectionResultUpdate


class DetectionResultRepository(BaseRepository[DetectionResult, DetectionResultCreate, DetectionResultUpdate]):
    """检测结果数据仓库类"""

    def __init__(self) -> None:
        """初始化检测结果仓库，绑定 DetectionResult 模型"""
        super().__init__(DetectionResult)

    def list_by_record(self, db: Session, *, record_id: UUID) -> list[DetectionResult]:
        """查询指定检测记录下的所有检测结果

        Args:
            db: 数据库会话
            record_id: 检测记录 UUID

        Returns:
            该检测记录关联的所有检测结果列表
        """
        statement = select(DetectionResult).where(DetectionResult.record_id == record_id)
        return list(db.scalars(statement).all())

    def list_by_class_id(self, db: Session, *, class_id: int, skip: int = 0, limit: int = 100) -> list[DetectionResult]:
        """根据缺陷类别 ID 分页查询检测结果

        Args:
            db: 数据库会话
            class_id: 缺陷类别 ID
            skip: 跳过的记录数，默认 0
            limit: 返回的最大记录数，默认 100

        Returns:
            符合指定类别 ID 的检测结果列表
        """
        statement = select(DetectionResult).where(DetectionResult.class_id == class_id).offset(skip).limit(limit)
        return list(db.scalars(statement).all())
