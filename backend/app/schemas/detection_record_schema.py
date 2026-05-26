"""检测记录（DetectionRecord）的 Pydantic 模型定义。

用于检测记录的创建、更新和读取场景的数据校验与序列化。
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DetectionRecordBase(BaseModel):
    """检测记录基础模型，包含检测记录的公共字段。"""

    model_config = ConfigDict(protected_namespaces=())

    user_id: UUID | None = None
    type: str
    status: str | None = "pending"
    model_name: str
    model_version: str | None = "1.0.0"
    total_objects: int | None = 0
    detection_time: float | None = None
    original_image_key: str | None = None
    result_image_key: str | None = None
    error_message: str | None = None


class DetectionRecordCreate(DetectionRecordBase):
    """检测记录创建模型，继承基础模型，用于接收创建检测记录的请求数据。"""

    pass


class DetectionRecordUpdate(BaseModel):
    """检测记录更新模型，所有字段可选，用于接收部分更新检测记录的请求数据。"""

    model_config = ConfigDict(protected_namespaces=())

    user_id: UUID | None = None
    type: str | None = None
    status: str | None = None
    model_name: str | None = None
    model_version: str | None = None
    total_objects: int | None = None
    detection_time: float | None = None
    original_image_key: str | None = None
    result_image_key: str | None = None
    error_message: str | None = None


class DetectionRecordRead(DetectionRecordBase):
    """检测记录读取模型，继承基础模型并附加 id 和时间戳字段，用于返回检测记录的响应数据。"""

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
