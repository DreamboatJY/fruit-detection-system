"""目标类别（TargetCategory）的 Pydantic 模型定义。

用于目标类别的创建、更新和读取场景的数据校验与序列化。
管理可检测缺陷类别的信息，包括名称、图标、颜色和排序等。
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TargetCategoryBase(BaseModel):
    """目标类别基础模型，包含目标类别的公共字段。"""

    name: str
    chinese_name: str
    description: str | None = None
    icon_url: str | None = None
    color: str | None = "#10b981"
    enabled: bool | None = True
    sort_order: int | None = 0


class TargetCategoryCreate(TargetCategoryBase):
    """目标类别创建模型，继承基础模型，用于接收创建目标类别的请求数据。"""

    pass


class TargetCategoryUpdate(BaseModel):
    """目标类别更新模型，所有字段可选，用于接收部分更新目标类别的请求数据。"""

    name: str | None = None
    chinese_name: str | None = None
    description: str | None = None
    icon_url: str | None = None
    color: str | None = None
    enabled: bool | None = None
    sort_order: int | None = None


class TargetCategoryRead(TargetCategoryBase):
    """目标类别读取模型，继承基础模型并附加 id 和时间戳字段，用于返回目标类别的响应数据。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
