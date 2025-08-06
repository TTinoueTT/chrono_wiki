"""
認証ユーティリティ

JWT生成・検証、パスワードハッシュ化などの認証関連機能を提供します。
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

# 設定
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ["REFRESH_TOKEN_EXPIRE_DAYS"])
JWT_ISSUER = os.environ.get("JWT_ISSUER")
JWT_AUDIENCE = os.environ.get("JWT_AUDIENCE")

# パスワードハッシュ化
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(client_password: str, hashed_password: str) -> bool:
    """パスワードを検証"""
    return pwd_context.verify(client_password, hashed_password)


def get_password_hash(client_password: str) -> str:
    """パスワードをハッシュ化"""
    return pwd_context.hash(client_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """アクセストークンを生成"""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update(
        {
            "exp": expire,
            "iat": now,  # 発行時刻を追加
            "iss": JWT_ISSUER,  # 発行者
            "aud": JWT_AUDIENCE,  # 対象者
            "type": "access",
        }
    )
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """リフレッシュトークンを生成"""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update(
        {
            "exp": expire,
            "iat": now,  # 発行時刻を追加
            "iss": JWT_ISSUER,  # 発行者
            "aud": JWT_AUDIENCE,  # 対象者
            "type": "refresh",
        }
    )
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """トークンを検証"""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,  # 発行者検証
            audience=JWT_AUDIENCE,  # 対象者検証
        )
        return payload
    except Exception:
        return None


def get_token_expires_in() -> int:
    """トークンの有効期限（秒）を取得"""
    return ACCESS_TOKEN_EXPIRE_MINUTES * 60
