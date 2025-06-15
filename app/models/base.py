from datetime import UTC, datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TimestampMixin:
    """タイムスタンプ用のMixinクラス"""
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )
