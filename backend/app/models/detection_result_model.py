"""
检测结果 ORM 模型

定义检测结果表的 SQLAlchemy ORM 模型，用于存储每次检测中识别出的每个目标详细信息。
"""
from uuid import UUID

from sqlalchemy import Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DetectionResult(Base):
    """检测结果模型，映射 detection_results 表"""

    __tablename__ = "detection_results"

    # 检测结果唯一标识，使用 UUID 并自动生成
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    # 关联的检测记录 ID，删除记录时级联删除相关结果
    record_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("detection_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # 检测框左上角 x 坐标
    x1: Mapped[float] = mapped_column(Float, nullable=False)
    # 检测框左上角 y 坐标
    y1: Mapped[float] = mapped_column(Float, nullable=False)
    # 检测框右下角 x 坐标
    x2: Mapped[float] = mapped_column(Float, nullable=False)
    # 检测框右下角 y 坐标
    y2: Mapped[float] = mapped_column(Float, nullable=False)
    # 检测置信度，范围 0~1
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    # 目标类别 ID
    class_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    # 目标类别英文名称
    class_name: Mapped[str] = mapped_column(String(50), nullable=False)
    # 目标类别中文名称
    chinese_name: Mapped[str | None] = mapped_column(String(50))
