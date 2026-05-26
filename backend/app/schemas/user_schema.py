"""用户（User）的 Pydantic 模型定义。

用于用户的创建、更新和读取场景的数据校验与序列化。
管理用户账号信息，包括用户名、邮箱、角色和头像等。
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    """用户基础模型，包含用户的公共字段。"""

    username: str
    email: str
    nickname: str | None = None
    role: str | None = "user"
    avatar_url: str | None = None
    is_active: bool | None = True


class UserCreate(UserBase):
    """用户创建模型，继承基础模型并附加密码字段，用于接收创建用户的请求数据。"""

    password_hash: str


class UserUpdate(BaseModel):
    """用户更新模型，所有字段可选，用于接收部分更新用户的请求数据。"""

    username: str | None = None
    email: str | None = None
    password_hash: str | None = None
    nickname: str | None = None
    role: str | None = None
    avatar_url: str | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    """用户读取模型，继承基础模型并附加 id 和时间戳字段，用于返回用户的响应数据。"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
