"""检测业务相关的 Pydantic 模型定义。

包含检测框、检测结果、单图检测响应、目标项和目标列表响应等模型，
主要用于检测 API 的请求与响应数据校验与序列化。
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class DetectionBox(BaseModel):
    """检测框信息，包含边界框坐标、置信度和类别标识。"""

    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int
    class_name: str


class DetectionResult(BaseModel):
    """检测结果，包含检测 ID、图片地址、检测框列表及模型元信息。"""

    model_config = ConfigDict(protected_namespaces=())

    detection_id: str
    image_url: str
    result_image_url: str
    boxes: List[DetectionBox]
    total_objects: int
    detection_time: float
    model_name: str
    created_at: datetime


class SingleDetectionResponse(BaseModel):
    """单图检测响应模型，包装检测结果并附带操作状态信息。"""

    success: bool
    message: str
    data: Optional[DetectionResult] = None


class TargetItem(BaseModel):
    """目标项模型，表示一个可检测的目标类别条目。"""

    id: int
    name: str
    chinese_name: str
    description: Optional[str] = None


class TargetListResponse(BaseModel):
    """目标列表响应模型，返回所有可检测目标类别的列表。"""

    success: bool
    message: str
    data: List[TargetItem]
