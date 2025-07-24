from datetime import UTC, datetime

from sqlalchemy import BigInteger, Column, DateTime
from sqlalchemy.orm import DeclarativeBase, validates


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """タイムスタンプ用のMixinクラス"""

    created_at = Column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class BaseModel(Base, TimestampMixin):
    """全てのモデルの基底クラス"""

    __abstract__ = True

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    @validates("id")
    def validate_id(self, key, value):
        if not isinstance(value, int):
            raise TypeError(f"{key} must be an integer")
        return value

    @validates("created_at", "updated_at")
    def validate_datetime(self, key, value):
        if not isinstance(value, datetime):
            raise TypeError(f"{key} must be a datetime object")
        return value
