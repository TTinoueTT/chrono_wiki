"""
ヘルスチェックルーター

システムの健全性を監視するためのエンドポイントを提供します。
"""

import os
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """基本的なヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "api_version": "v1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """詳細なヘルスチェックエンドポイント"""
    start_time = time.time()

    # 基本情報
    health_info: dict = {
        "status": "healthy",
        "version": "1.0.0",
        "api_version": "v1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "checks": {},
    }

    # データベース接続チェック
    try:
        db_start_time = time.time()
        db.execute(text("SELECT 1"))
        db_time = time.time() - db_start_time

        health_info["checks"]["database"] = {
            "status": "healthy",
            "response_time_ms": round(db_time * 1000, 2),
            "connection": "active",
        }
    except Exception as e:
        health_info["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
            "connection": "failed",
        }
        health_info["status"] = "degraded"

    # 認証システムチェック
    try:
        auth_start_time = time.time()
        api_key = os.getenv("API_KEY", "dev_sk_default")
        secret_key = os.getenv("SECRET_KEY")

        auth_time = time.time() - auth_start_time

        health_info["checks"]["authentication"] = {
            "status": "healthy",
            "response_time_ms": round(auth_time * 1000, 2),
            "api_key_configured": bool(api_key),
            "secret_key_configured": bool(secret_key),
            "auth_types": ["api_key", "jwt"],
        }
    except Exception as e:
        health_info["checks"]["authentication"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        health_info["status"] = "degraded"

    # 環境変数チェック
    required_env_vars = ["DATABASE_URL", "SECRET_KEY", "API_KEY"]

    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    health_info["checks"]["environment"] = {
        "status": "healthy" if not missing_vars else "unhealthy",
        "missing_variables": missing_vars,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug_mode": os.getenv("DEBUG", "false").lower() == "true",
    }

    if missing_vars:
        health_info["status"] = "degraded"

    # システムリソースチェック（オプショナル）
    system_check = await _check_system_resources()
    health_info["checks"]["system"] = system_check

    # 全体の処理時間
    total_time = time.time() - start_time
    health_info["response_time_ms"] = round(total_time * 1000, 2)

    # ステータスコードの決定
    if health_info["status"] == "healthy":
        return health_info
    elif health_info["status"] == "degraded":
        return JSONResponse(status_code=status.HTTP_200_OK, content=health_info)
    else:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=health_info)


async def _check_system_resources() -> dict:
    """システムリソースチェック（オプショナル）"""
    try:
        import psutil

        return {
            "status": "healthy",
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
        }
    except ImportError:
        return {
            "status": "unknown",
            "note": "psutil not available - install with: pip install psutil",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness Probe（準備完了チェック）"""
    try:
        # データベース接続テスト
        db.execute(text("SELECT 1"))

        # 必須環境変数の確認
        required_vars = ["DATABASE_URL", "SECRET_KEY"]
        for var in required_vars:
            if not os.getenv(var):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Required environment variable {var} is not set",
                )

        return {
            "status": "ready",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {"database": "ready", "environment": "ready"},
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}",
        )


@router.get("/health/live")
async def liveness_check():
    """Liveness Probe（生存チェック）"""
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": "running",
    }


@router.get("/health/auth")
async def auth_health_check():
    """認証システム専用ヘルスチェック"""
    try:
        api_key = os.getenv("API_KEY", "dev_sk_default")
        secret_key = os.getenv("SECRET_KEY")

        auth_status = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "auth_systems": {
                "api_key": {
                    "status": "configured" if api_key else "not_configured",
                    "key_length": len(api_key) if api_key else 0,
                },
                "jwt": {
                    "status": "configured" if secret_key else "not_configured",
                    "algorithm": os.getenv("ALGORITHM", "HS256"),
                },
            },
            "supported_auth_types": ["api_key", "jwt"],
            "environment": os.getenv("ENVIRONMENT", "development"),
        }

        # 設定が不完全な場合は警告
        if not api_key or not secret_key:
            auth_status["status"] = "degraded"
            auth_status["warnings"] = []
            if not api_key:
                auth_status["warnings"].append("API_KEY not configured")
            if not secret_key:
                auth_status["warnings"].append("SECRET_KEY not configured")

        return auth_status

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


@router.get("/health/simple")
async def simple_health_check():
    """シンプルなヘルスチェック（軽量版）"""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
