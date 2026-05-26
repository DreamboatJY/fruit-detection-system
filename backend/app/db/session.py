"""数据库会话管理模块。

提供 SQLAlchemy 数据库引擎、会话工厂以及 FastAPI 依赖注入
函数 get_db，确保每个请求使用独立的数据库会话并在请求结束后自动关闭。
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

# 根据配置构建 PostgreSQL 连接 URL
database_url = URL.create(
    drivername="postgresql+psycopg2",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)

# 创建数据库引擎，启用连接池心跳检测、设置池大小与溢出上限
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    future=True,
)

# 创建会话工厂，默认不自动提交、不自动刷新
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖注入函数，为每个请求提供独立的数据库会话。

    Yields:
        Session: SQLAlchemy 会话实例。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
