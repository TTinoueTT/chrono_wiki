import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .models.base import Base

# データベースURL（環境変数から取得、デフォルトはSQLite）
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# エンジン作成
engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    ),
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    # MySQL用の設定
    pool_pre_ping=True if "mysql" in DATABASE_URL else False,
    echo=os.getenv("DEBUG", "0") == "1",  # デバッグ時にSQLログ出力
)

# セッションファクトリ作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """データベースセッションを取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """テーブルを作成"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """テーブルを削除"""
    Base.metadata.drop_all(bind=engine)
 