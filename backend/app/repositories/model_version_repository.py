"""
模型版本数据仓库模块

提供 ModelVersion 模型特有的数据库查询方法，
包括查询活跃版本和按名称+版本号精确查找。
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.model_version_model import ModelVersion
from app.repositories.base_repository import BaseRepository
from app.schemas.model_version_schema import ModelVersionCreate, ModelVersionUpdate


class ModelVersionRepository(BaseRepository[ModelVersion, ModelVersionCreate, ModelVersionUpdate]):
    """模型版本数据仓库类"""

    def __init__(self) -> None:
        """初始化模型版本仓库，绑定 ModelVersion 模型"""
        super().__init__(ModelVersion)

    def list_active(self, db: Session) -> list[ModelVersion]:
        """查询所有状态为 active（活跃）的模型版本

        Args:
            db: 数据库会话

        Returns:
            活跃状态的模型版本列表
        """
        statement = select(ModelVersion).where(ModelVersion.status == "active")
        return list(db.scalars(statement).all())

    def get_by_name_and_version(self, db: Session, *, name: str, version: str) -> ModelVersion | None:
        """根据模型名称和版本号精确查找模型版本

        Args:
            db: 数据库会话
            name: 模型名称
            version: 版本号

        Returns:
            匹配的模型版本实例，未找到时返回 None
        """
        statement = select(ModelVersion).where(ModelVersion.name == name, ModelVersion.version == version)
        return db.scalar(statement)
