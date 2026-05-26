"""
基础数据仓库模块

提供泛型 CRUD 基类 BaseRepository，封装通用的数据库增删改查操作，
具体业务 Repository 通过继承该类复用基础逻辑。
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    SQLAlchemy 通用 CRUD 基类

    通过泛型参数绑定模型类型、创建模式和更新模式，提供开箱即用的
    get / list / create / update / delete 方法。
    """

    def __init__(self, model: type[ModelType]) -> None:
        """初始化基础仓库

        Args:
            model: SQLAlchemy 模型类
        """
        self.model = model

    def get(self, db: Session, id: Any) -> ModelType | None:
        """根据主键 ID 查询单条记录

        Args:
            db: 数据库会话
            id: 主键值

        Returns:
            匹配的模型实例，未找到时返回 None
        """
        return db.get(self.model, id)

    def list(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """分页查询所有记录

        Args:
            db: 数据库会话
            skip: 跳过的记录数，默认 0
            limit: 返回的最大记录数，默认 100

        Returns:
            模型实例列表
        """
        statement = select(self.model).offset(skip).limit(limit)
        return list(db.scalars(statement).all())

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """创建新记录

        Args:
            db: 数据库会话
            obj_in: 创建数据模式（Pydantic 模型）

        Returns:
            创建后的模型实例
        """
        db_obj = self.model(**obj_in.model_dump(exclude_unset=True))
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """更新已有记录

        仅更新 obj_in 中显式设置的字段，未设置的字段保持不变。

        Args:
            db: 数据库会话
            db_obj: 待更新的数据库模型实例
            obj_in: 更新数据模式（Pydantic 模型）

        Returns:
            更新后的模型实例
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: Any) -> ModelType | None:
        """根据主键 ID 删除记录

        Args:
            db: 数据库会话
            id: 主键值

        Returns:
            被删除的模型实例，未找到时返回 None
        """
        db_obj = self.get(db, id)
        if db_obj is None:
            return None
        db.delete(db_obj)
        db.flush()
        return db_obj
