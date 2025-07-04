"""
ユーザーモデル

認証・認可システムで使用するユーザーエンティティを定義します。
"""

import uuid
from typing import Optional

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """ユーザーモデル"""

    __tablename__ = "users"

    # 基本識別フィールド
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # プロフィール情報
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # セキュリティ・認証
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 権限・ロール
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)

    # セキュリティ監視
    last_login: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    failed_login_attempts: Mapped[str] = mapped_column(String(10), default="0", nullable=False)
    locked_until: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    def __repr__(self):
        """文字列表現"""
        return f"<User(id='{self.id}', username='{self.username}', email='{self.email}')>"
