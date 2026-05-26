"""
缺陷目标类别数据仓库模块

提供 TargetCategory 模型特有的数据库查询方法，
包括查询已启用的类别列表和按名称查找类别。
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.target_category_model import TargetCategory
from app.repositories.base_repository import BaseRepository
from app.schemas.target_category_schema import TargetCategoryCreate, TargetCategoryUpdate


class TargetCategoryRepository(BaseRepository[TargetCategory, TargetCategoryCreate, TargetCategoryUpdate]):
    """缺陷目标类别数据仓库类"""

    def __init__(self) -> None:
        """初始化目标类别仓库，绑定 TargetCategory 模型"""
        super().__init__(TargetCategory)

    def list_enabled(self, db: Session) -> list[TargetCategory]:
        """查询所有已启用的缺陷类别，按排序号和 ID 升序排列

        Args:
            db: 数据库会话

        Returns:
            已启用的缺陷类别列表
        """
        statement = (
            select(TargetCategory)
            .where(TargetCategory.enabled.is_(True))
            .order_by(TargetCategory.sort_order.asc(), TargetCategory.id.asc())
        )
        return list(db.scalars(statement).all())

    def get_by_name(self, db: Session, *, name: str) -> TargetCategory | None:
        """根据类别名称精确查找

        Args:
            db: 数据库会话
            name: 类别名称

        Returns:
            匹配的类别实例，未找到时返回 None
        """
        return db.scalar(select(TargetCategory).where(TargetCategory.name == name))
