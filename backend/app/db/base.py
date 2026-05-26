"""SQLAlchemy 声明式基类与模型导入模块。

定义所有 ORM 模型共用的 DeclarativeBase，并提供 import_all_models
函数确保模型被注册到 Base.metadata 上，供 Alembic 等工具使用。
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类，所有 ORM 模型应继承此类。"""


def import_all_models() -> None:
    """导入所有 ORM 模型，确保 Base.metadata 能够发现所有映射表。

    在 Alembic 迁移或元数据操作前调用此函数，避免因模型未导入
    导致元数据不完整的问题。
    """
    from app.models import detection_record_model  # noqa: F401
    from app.models import detection_result_model  # noqa: F401
    from app.models import model_version_model  # noqa: F401
    from app.models import target_category_model  # noqa: F401
    from app.models import user_model  # noqa: F401
