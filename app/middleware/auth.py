"""
認証ミドルウェア

ハイブリッド認証システム（APIキー + JWT）のミドルウェアを提供します。
"""

import os
from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..auth.utils import verify_token as verify_jwt_token


class HybridAuthMiddleware(BaseHTTPMiddleware):
    """ハイブリッド認証ミドルウェア"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 認証不要なエンドポイントをチェック
        if self._is_auth_exempt(request.url.path):
            return await call_next(request)

        # 基本認証チェック
        auth_info = await self._basic_auth_check(request)

        if auth_info is None:
            return JSONResponse(status_code=401, content={"detail": "Authentication required"})

        # 認証情報をリクエストに追加
        request.state.auth_info = auth_info

        return await call_next(request)

    async def _basic_auth_check(self, request: Request) -> Optional[dict]:
        """基本認証チェック"""
        # 1. X-API-Key認証（最優先）
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return self._verify_api_key(api_key)

        # 2. JWT認証
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return self._verify_jwt_basic(auth_header)

        return None

    def _verify_api_key(self, api_key: str) -> Optional[dict]:
        """APIキー認証の基本検証"""
        expected_key = os.getenv("API_KEY", "dev_sk_default")

        if api_key == expected_key:
            return {"type": "api_key", "verified": True, "api_key": api_key, "user_id": "system", "role": "admin"}

        return None

    def _verify_jwt_basic(self, auth_header: str) -> Optional[dict]:
        """JWT認証の基本検証"""
        try:
            token = auth_header.replace("Bearer ", "")
            payload = verify_jwt_token(token)

            if payload:
                return {
                    "type": "jwt",
                    "verified": True,
                    "token": token,
                    "payload": payload,
                    "user_id": payload.get("sub"),
                    "role": payload.get("role", "user"),
                }
        except Exception:
            pass

        return None

    def _is_auth_exempt(self, path: str) -> bool:
        """認証不要なパスかどうかを判定"""
        exempt_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
        ]
        return any(path.startswith(exempt_path) for exempt_path in exempt_paths)
