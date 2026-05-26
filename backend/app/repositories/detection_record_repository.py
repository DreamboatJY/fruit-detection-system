"""
检测记录数据仓库模块

提供 DetectionRecord 模型特有的数据库查询方法，
包括按用户查询和按状态查询。
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.detection_record_model import DetectionRecord
from app.repositories.base_repository import BaseRepository
from app.schemas.detection_record_schema import DetectionRecordCreate, DetectionRecordUpdate


class DetectionRecordRepository(BaseRepository[DetectionRecord, DetectionRecordCreate, DetectionRecordUpdate]):
    """检测记录数据仓库类"""

    def __init__(self) -> None:
        """初始化检测记录仓库，绑定 DetectionRecord 模型"""
        super().__init__(DetectionRecord)

    def list_by_user(self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100) -> list[DetectionRecord]:
        """查询指定用户的所有检测记录，按创建时间倒序排列

        Args:
            db: 数据库会话
            user_id: 用户 UUID
            skip: 跳过的记录数，默认 0
            limit: 返回的最大记录数，默认 100

        Returns:
            该用户的检测记录列表
        """
        statement = (
            select(DetectionRecord)
            .where(DetectionRecord.user_id == user_id)
            .order_by(DetectionRecord.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(statement).all())

    def list_by_status(self, db: Session, *, status: str, skip: int = 0, limit: int = 100) -> list[DetectionRecord]:
        """根据检测状态查询记录，按创建时间倒序排列

        Args:
            db: 数据库会话
            status: 检测状态（如 pending / processing / completed / failed）
            skip: 跳过的记录数，默认 0
            limit: 返回的最大记录数，默认 100

        Returns:
            符合指定状态的检测记录列表
        """
        statement = (
            select(DetectionRecord)
            .where(DetectionRecord.status == status)
            .order_by(DetectionRecord.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(statement).all())
