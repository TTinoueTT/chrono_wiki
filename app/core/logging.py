"""
FastAPI用ログ設定

参考: https://apidog.com/jp/blog/version-2-logging-endpoints-with-python-fastapi/
"""

import logging
import logging.config
import os
import time
from pathlib import Path
from typing import Any, Dict

# ログディレクトリの確認・作成
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)


def get_logging_config() -> Dict[str, Any]:
    """ログ設定を取得"""

    # 環境変数からログレベルを取得
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # タイムゾーンをJSTに設定
    os.environ["TZ"] = "Asia/Tokyo"
    time.tzset()

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(levelname)s - %(message)s",
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "request": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s - IP: %(client_ip)s - Method: %(method)s - Path: %(path)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "detailed",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "access_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": "logs/access.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "auth_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": "logs/auth.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "": {  # ルートロガー
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "app": {  # アプリケーションロガー
                "handlers": ["console", "file", "error_file"],
                "level": log_level,
                "propagate": False,
            },
            "app.auth": {  # 認証ロガー
                "handlers": ["console", "file", "error_file", "auth_file"],
                "level": log_level,
                "propagate": False,
            },
            "app.middleware": {  # ミドルウェアロガー
                "handlers": ["console", "file", "access_file"],
                "level": log_level,
                "propagate": False,
            },
            "app.routers": {  # ルーターロガー
                "handlers": ["console", "file", "access_file"],
                "level": log_level,
                "propagate": True,
                # "propagate": False,
            },
            "app.services": {  # サービスロガー
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "app.crud": {  # CRUDロガー
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn": {  # Uvicornロガー
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {  # Uvicornアクセスロガー
                "handlers": ["access_file"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }


def setup_logging():
    """ログ設定を初期化"""
    config = get_logging_config()
    logging.config.dictConfig(config)

    # ログ設定完了を記録
    logger = logging.getLogger("app")
    logger.info("Logging configuration initialized")


def get_logger(name: str) -> logging.Logger:
    """指定された名前のロガーを取得"""
    return logging.getLogger(f"app.{name}")


# 環境別のログ設定
def setup_development_logging():
    """開発環境用のログ設定"""
    os.environ["LOG_LEVEL"] = "DEBUG"
    setup_logging()


def setup_production_logging():
    """本番環境用のログ設定"""
    os.environ["LOG_LEVEL"] = "INFO"
    setup_logging()


def setup_test_logging():
    """テスト環境用のログ設定"""
    os.environ["LOG_LEVEL"] = "WARNING"
    setup_logging()


# カスタムログフィルター
class RequestLogFilter(logging.Filter):
    """リクエスト情報を含むログフィルター"""

    def __init__(self):
        super().__init__()
        self.client_ip = None
        self.method = None
        self.path = None

    def filter(self, record):
        record.client_ip = getattr(self, "client_ip", "unknown")
        record.method = getattr(self, "method", "unknown")
        record.path = getattr(self, "path", "unknown")
        return True
