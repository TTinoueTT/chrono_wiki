"""
ログミドルウェア

参考: https://apidog.com/jp/blog/version-2-logging-endpoints-with-python-fastapi/
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..core import get_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """リクエストログミドルウェア"""

    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("middleware.logging")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # リクエスト開始時間
        start_time = time.time()

        # クライアントIPアドレスを取得
        client_ip = request.client.host if request.client else "unknown"

        # リクエスト情報をログに記録
        self.logger.info(
            f"受信リクエスト: {request.method} {request.url.path} - "
            f"IP: {client_ip} - "
            f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
        )

        # リクエスト処理
        response = await call_next(request)

        # 処理時間を計算
        process_time = time.time() - start_time

        # レスポンス情報をログに記録
        self.logger.info(
            f"レスポンス完了: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Process Time: {process_time:.3f}s"
        )

        return response


def log_request_middleware(request: Request, call_next: Callable) -> Response:
    """
    関数ベースのリクエストログミドルウェア

    参考リンクの実装例に基づく
    """
    logger = get_logger("middleware.request")

    # リクエスト情報をログに記録
    logger.info(f"受信リクエスト：{request.method} {request.url}")

    # リクエスト処理
    response = call_next(request)

    # レスポンス情報をログに記録
    logger.info(f"レスポンスステータス：{response.status_code}")

    return response
