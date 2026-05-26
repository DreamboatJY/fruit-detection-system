"""
检测记录 ORM 模型

定义检测记录表的 SQLAlchemy ORM 模型，用于存储每次检测任务的完整信息。
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DetectionRecord(Base):
    """检测记录模型，映射 detection_records 表"""

    __tablename__ = "detection_records"

    # 检测记录唯一标识，使用 UUID 并自动生成
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    # 关联的用户 ID，删除用户时级联删除相关记录
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # 检测类型，如 image/video
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    # 检测状态，如 pending/processing/completed/failed，默认为 pending
    status: Mapped[str | None] = mapped_column(String(20), server_default="pending", index=True)
    # 使用的模型名称
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    # 使用的模型版本号，默认为 1.0.0
    model_version: Mapped[str | None] = mapped_column(String(20), server_default="1.0.0")
    # 检测出的目标总数
    total_objects: Mapped[int | None] = mapped_column(Integer, server_default="0")
    # 检测耗时（秒）
    detection_time: Mapped[float | None] = mapped_column(Float)
    # 原始图像在对象存储中的 key
    original_image_key: Mapped[str | None] = mapped_column(String(500))
    # 检测结果图像在对象存储中的 key
    result_image_key: Mapped[str | None] = mapped_column(String(500))
    # 检测失败时的错误信息
    error_message: Mapped[str | None] = mapped_column(Text)
    # 记录创建时间
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.current_timestamp(), index=True)
    # 记录更新时间，每次更新时自动刷新
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
