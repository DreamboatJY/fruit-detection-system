"""检测结果（DetectionResult）的 Pydantic 模型定义。

用于检测结果条目的创建、更新和读取场景的数据校验与序列化。
每条检测结果对应一个检测框，关联到某次检测记录。
"""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DetectionResultBase(BaseModel):
    """检测结果基础模型，包含单个检测框的坐标、置信度和类别信息。"""

    record_id: UUID
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int
    class_name: str
    chinese_name: str | None = None


class DetectionResultCreate(DetectionResultBase):
    """检测结果创建模型，继承基础模型，用于接收创建检测结果的请求数据。"""

    pass


class DetectionResultUpdate(BaseModel):
    """检测结果更新模型，所有字段可选，用于接收部分更新检测结果的请求数据。"""

    record_id: UUID | None = None
    x1: float | None = None
    y1: float | None = None
    x2: float | None = None
    y2: float | None = None
    confidence: float | None = None
    class_id: int | None = None
    class_name: str | None = None
    chinese_name: str | None = None


class DetectionResultRead(DetectionResultBase):
    """检测结果读取模型，继承基础模型并附加 id 字段，用于返回检测结果的响应数据。"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
