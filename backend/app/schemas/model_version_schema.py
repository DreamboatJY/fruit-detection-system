"""模型版本（ModelVersion）的 Pydantic 模型定义。

用于模型版本的创建、更新和读取场景的数据校验与序列化。
管理检测模型的版本信息，包括名称、版本号、描述和存储路径等。
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ModelVersionBase(BaseModel):
    """模型版本基础模型，包含模型版本的公共字段。"""

    model_config = ConfigDict(protected_namespaces=())

    name: str
    version: str
    description: str | None = None
    model_key: str | None = None
    status: str | None = "active"


class ModelVersionCreate(ModelVersionBase):
    """模型版本创建模型，继承基础模型，用于接收创建模型版本的请求数据。"""

    pass


class ModelVersionUpdate(BaseModel):
    """模型版本更新模型，所有字段可选，用于接收部分更新模型版本的请求数据。"""

    model_config = ConfigDict(protected_namespaces=())

    name: str | None = None
    version: str | None = None
    description: str | None = None
    model_key: str | None = None
    status: str | None = None


class ModelVersionRead(ModelVersionBase):
    """模型版本读取模型，继承基础模型并附加 id 和时间戳字段，用于返回模型版本的响应数据。"""

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
