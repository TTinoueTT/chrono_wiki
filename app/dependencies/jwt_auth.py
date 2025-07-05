"""
認証依存性

JWT認証と権限チェックの依存性関数を提供します。
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..auth.utils import verify_token
from ..database import get_db
from ..models.user import User

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """現在のユーザーを取得（認証が任意）"""
    if not credentials:
        return None

    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    return user


def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user),
) -> User:
    """現在のアクティブユーザーを取得（認証必須）"""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    return current_user


def require_auth(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """認証を要求"""
    return current_user


def require_moderator(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """モデレーター権限を要求"""
    if current_user.role not in ["moderator", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Moderator privileges required")
    return current_user


def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """管理者権限を要求"""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user


def optional_auth(
    current_user: Optional[User] = Depends(get_current_user),
) -> Optional[User]:
    """オプショナル認証（認証があればユーザーを返す、なければNone）"""
    return current_user
