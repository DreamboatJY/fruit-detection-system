"""
用户数据仓库模块

提供 User 模型特有的数据库查询方法，
包括按邮箱和按用户名查询用户。
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.repositories.base_repository import BaseRepository
from app.schemas.user_schema import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """用户数据仓库类"""

    def __init__(self) -> None:
        """初始化用户仓库，绑定 User 模型"""
        super().__init__(User)

    def get_by_email(self, db: Session, *, email: str) -> User | None:
        """根据邮箱地址查找用户

        Args:
            db: 数据库会话
            email: 用户邮箱

        Returns:
            匹配的用户实例，未找到时返回 None
        """
        return db.scalar(select(User).where(User.email == email))

    def get_by_username(self, db: Session, *, username: str) -> User | None:
        """根据用户名查找用户

        Args:
            db: 数据库会话
            username: 用户名

        Returns:
            匹配的用户实例，未找到时返回 None
        """
        return db.scalar(select(User).where(User.username == username))
