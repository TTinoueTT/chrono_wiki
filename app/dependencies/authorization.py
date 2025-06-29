"""
認証依存性モジュール

FastAPIアプリケーション全体に適用する認証機能を提供します。
"""

import os

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

# APIキーヘッダー設定
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)


def verify_token(auth_header: str = Depends(api_key_header)):
    """
    APIキーを検証する依存性関数

    Args:
        auth_header: Authorizationヘッダーの値

    Returns:
        str: 検証されたAPIキー

    Raises:
        HTTPException: APIキーが無効な場合
    """
    # 環境変数からAPIキーを取得
    expected_key = os.getenv("API_KEY", "dev_sk_default")

    if auth_header != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_header


def optional_verify_token(auth_header: str = Depends(api_key_header)):
    """
    オプショナルなAPIキー検証（認証があれば検証、なければスキップ）

    Args:
        auth_header: Authorizationヘッダーの値

    Returns:
        str: 検証されたAPIキー（認証がない場合はNone）
    """
    expected_key = os.getenv("API_KEY", "dev_sk_default")

    if auth_header != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_header
