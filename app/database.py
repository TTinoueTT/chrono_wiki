import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .models.base import Base

# データベースURL（環境変数から取得）
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")


# PostgreSQL 17用の最適化設定
def get_connect_args(database_url: str) -> dict:
    """データベース別の接続設定を取得"""
    if "sqlite" in database_url:
        return {"check_same_thread": False}
    elif "postgresql" in database_url:
        return {
            "application_name": "fastapi_timeline",  # 接続識別用
            "options": "-c timezone=utc",  # UTCタイムゾーン設定
        }
    return {}


def get_pool_settings(database_url: str) -> dict:
    """データベース別のプール設定を取得"""
    if "sqlite" in database_url:
        return {
            "poolclass": StaticPool,
            "pool_pre_ping": False,
        }
    elif "postgresql" in database_url:
        return {
            "pool_pre_ping": True,  # PostgreSQL 17の接続確認機能
            "pool_size": 20,  # 接続プールサイズ
            "max_overflow": 30,  # 最大オーバーフロー接続数
            "pool_recycle": 3600,  # 1時間で接続をリサイクル
        }
    return {}


# エンジン作成
engine = create_engine(
    DATABASE_URL,
    connect_args=get_connect_args(DATABASE_URL),
    **get_pool_settings(DATABASE_URL),
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


def get_database_info() -> dict:
    """データベース情報を取得（PostgreSQL 17の新機能を活用）"""
    if not DATABASE_URL:
        return {"type": "Unknown", "error": "DATABASE_URL not set"}

    if "postgresql" in DATABASE_URL:
        return {
            "type": "PostgreSQL",
            "version": "17.x",
            "features": [
                "Enhanced JSONB operations",
                "Improved MERGE functionality",
                "Better vacuum performance",
                "Enhanced logical replication",
                "Optimized I/O layer",
                "Advanced query execution",
            ],
        }
    elif "sqlite" in DATABASE_URL:
        return {
            "type": "SQLite",
            "version": "3.x",
            "features": ["Development mode"],
        }
    return {"type": "Unknown"}
