"""db 包入口，导出 SQLAlchemy 基类与模型导入工具函数。

暴露 Base 与 import_all_models 供应用其他模块统一引用。
"""

from app.db.base import Base, import_all_models

__all__ = ["Base", "import_all_models"]
