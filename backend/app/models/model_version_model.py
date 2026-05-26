"""
模型版本 ORM 模型

定义模型版本表的 SQLAlchemy ORM 模型，用于管理检测模型的版本信息。
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ModelVersion(Base):
    """模型版本信息模型，映射 model_versions 表"""

    __tablename__ = "model_versions"
    # 联合唯一约束：同一模型名称下不允许重复版本号
    __table_args__ = (UniqueConstraint("name", "version", name="uq_model_versions_name_version"),)

    # 版本记录唯一标识，使用 UUID 并自动生成
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    # 模型名称
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    # 版本号，如 "1.0.0"
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    # 版本说明描述
    description: Mapped[str | None] = mapped_column(Text)
    # 模型文件在对象存储中的 key
    model_key: Mapped[str | None] = mapped_column(String(500))
    # 模型状态，如 active/inactive，默认为 active
    status: Mapped[str | None] = mapped_column(String(20), server_default="active", index=True)
    # 记录创建时间
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.current_timestamp())
    # 记录更新时间，每次更新时自动刷新
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
