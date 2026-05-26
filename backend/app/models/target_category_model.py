"""
目标类别 ORM 模型

定义目标类别表的 SQLAlchemy ORM 模型，用于管理所有可检测的缺陷类别配置。
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TargetCategory(Base):
    """目标类别模型，映射 target_categories 表"""

    __tablename__ = "target_categories"

    # 类别唯一标识，自增主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 类别英文名称，唯一
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    # 类别中文名称，唯一
    chinese_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    # 类别描述说明
    description: Mapped[str | None] = mapped_column(Text)
    # 类别图标 URL 地址
    icon_url: Mapped[str | None] = mapped_column(String(500))
    # 类别标识颜色，默认为绿色
    color: Mapped[str | None] = mapped_column(String(20), server_default="#10b981")
    # 是否启用，默认为启用
    enabled: Mapped[bool | None] = mapped_column(Boolean, server_default="true", index=True)
    # 排序权重，数值越小越靠前
    sort_order: Mapped[int | None] = mapped_column(Integer, server_default="0", index=True)
    # 记录创建时间
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.current_timestamp())
    # 记录更新时间，每次更新时自动刷新
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
