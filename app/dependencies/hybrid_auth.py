"""
ハイブリッド認証依存性

APIキー認証とJWT認証を統合した認証依存性を提供します。
"""

from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..enums import UserRole
from ..models.user import User
from ..services.user import user_service


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """詳細なユーザー認証（依存性で処理）"""

    auth_info = getattr(request.state, "auth_info", None)

    if not auth_info or not auth_info.get("verified"):
        return None

    # APIキー認証の場合
    if auth_info["type"] == "api_key":
        return create_api_user(auth_info)

    # JWT認証の場合
    elif auth_info["type"] == "jwt":
        return verify_jwt_user(auth_info, db)

    return None


def create_api_user(auth_info: dict) -> User:
    """APIキー認証用のシステムユーザーを作成"""
    return User(
        id="system",
        username="system",
        email="system@api.local",
        hashed_password="",  # APIキー認証なのでパスワードは不要
        role=UserRole.ADMIN.value,
        is_active=True,
    )


def verify_jwt_user(auth_info: dict, db: Session) -> Optional[User]:
    """JWT認証の詳細検証"""
    user_id = auth_info.get("user_id")
    if not user_id:
        return None

    user = user_service.get_user(db, user_id)
    if not user or not user.is_active:
        return None

    return user


# 権限チェック依存性
def require_auth(current_user: User = Depends(get_current_user)) -> User:
    """認証を要求"""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return current_user


def require_moderator(current_user: User = Depends(get_current_user)) -> User:
    """モデレーター権限を要求"""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    if not UserRole.has_permission(current_user.role, UserRole.MODERATOR.value):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Moderator privileges required")
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """管理者権限を要求"""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    if not UserRole.has_permission(current_user.role, UserRole.ADMIN.value):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user


def optional_auth(current_user: User = Depends(get_current_user)) -> Optional[User]:
    """オプショナルな認証（認証があればユーザーを返す）"""
    return current_user
