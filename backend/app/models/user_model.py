"""
用户 ORM 模型

定义用户表的 SQLAlchemy ORM 模型，用于管理平台用户信息。
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """用户模型，映射 users 表"""

    __tablename__ = "users"

    # 用户唯一标识，使用 UUID 并自动生成
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    # 用户名，唯一且不可为空
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    # 邮箱地址，唯一且不可为空
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    # 密码哈希值
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # 用户昵称，可选
    nickname: Mapped[str | None] = mapped_column(String(50))
    # 用户角色，默认为普通用户
    role: Mapped[str | None] = mapped_column(String(20), server_default="user")
    # 头像 URL 地址
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    # 是否启用，默认为启用状态
    is_active: Mapped[bool | None] = mapped_column(Boolean, server_default="true")
    # 记录创建时间
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.current_timestamp())
    # 记录更新时间，每次更新时自动刷新
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
