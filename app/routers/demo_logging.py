"""
ログ出力デモルーター

参考: https://apidog.com/jp/blog/version-2-logging-endpoints-with-python-fastapi/
"""

import time

from fastapi import APIRouter, HTTPException, Request, status

from ..core import get_logger

router = APIRouter(tags=["demo"])

# 各ロガーの初期化
logger = get_logger("routers.demo")
auth_logger = get_logger("auth")
service_logger = get_logger("services")
crud_logger = get_logger("crud")


@router.get("/demo/logging")
async def demo_logging():
    """
    ログ出力のデモエンドポイント

    参考リンクの実装例に基づく
    """
    logger.info("ログデモエンドポイントが呼び出されました")

    # 各ログレベルのデモ
    logger.debug("これはDEBUGレベルのログです")
    logger.info("これはINFOレベルのログです")
    logger.warning("これはWARNINGレベルのログです")
    logger.error("これはERRORレベルのログです")

    return {"message": "ログデモが実行されました", "logs": "logs/app.log と logs/error.log を確認してください"}


@router.get("/demo/auth-logging")
async def demo_auth_logging():
    """認証ログのデモ"""
    auth_logger.info("認証ログデモ: ユーザーログイン試行")
    auth_logger.warning("認証ログデモ: 無効なパスワード試行")
    auth_logger.error("認証ログデモ: アカウントロック")

    return {"message": "認証ログデモが実行されました", "logs": "logs/auth.log を確認してください"}


@router.get("/demo/service-logging")
async def demo_service_logging():
    """サービスログのデモ"""
    service_logger.info("サービスログデモ: データベース接続確立")
    service_logger.info("サービスログデモ: クエリ実行開始")
    service_logger.info("サービスログデモ: クエリ実行完了")

    return {"message": "サービスログデモが実行されました", "logs": "logs/app.log を確認してください"}


@router.get("/demo/crud-logging")
async def demo_crud_logging():
    """CRUDログのデモ"""
    crud_logger.info("CRUDログデモ: 人物データ取得開始")
    crud_logger.debug("CRUDログデモ: SQLクエリ実行")
    crud_logger.info("CRUDログデモ: 人物データ取得完了")

    return {"message": "CRUDログデモが実行されました", "logs": "logs/app.log を確認してください"}


@router.get("/demo/error-logging")
async def demo_error_logging():
    """エラーログのデモ"""
    try:
        # 意図的にエラーを発生させる
        _ = 1 / 0
    except ZeroDivisionError as e:
        logger.error(f"エラーログデモ: ゼロ除算エラーが発生しました: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="意図的なエラーです")

    return {"message": "このメッセージは表示されません"}


@router.get("/demo/request-info")
async def demo_request_info(request: Request):
    """リクエスト情報のログデモ"""
    # リクエスト情報をログに記録
    logger.info(f"リクエスト情報: {request.method} {request.url}")
    logger.info(f"クライアントIP: {request.client.host if request.client else 'unknown'}")
    logger.info(f"User-Agent: {request.headers.get('user-agent', 'unknown')}")

    return {
        "message": "リクエスト情報がログに記録されました",
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host if request.client else "unknown",
    }


@router.post("/demo/performance-logging")
async def demo_performance_logging():
    """パフォーマンスログのデモ"""
    start_time = time.time()

    # 処理時間をシミュレート
    time.sleep(0.5)

    process_time = time.time() - start_time
    logger.info(f"パフォーマンスログデモ: 処理時間 {process_time:.3f}秒")

    return {"message": "パフォーマンスログデモが実行されました", "process_time": f"{process_time:.3f}秒"}


@router.get("/demo/structured-logging")
async def demo_structured_logging():
    """構造化ログのデモ"""
    # 構造化されたログ情報
    log_data = {
        "user_id": "demo_user_123",
        "action": "data_retrieval",
        "resource": "persons",
        "count": 25,
        "status": "success",
    }

    logger.info(f"構造化ログデモ: {log_data}")

    return {"message": "構造化ログデモが実行されました", "log_data": log_data}


@router.get("/demo/log-levels")
async def demo_log_levels():
    """ログレベル別のデモ"""
    # 各ログレベルのメッセージ
    logger.debug("DEBUG: 詳細なデバッグ情報")
    logger.info("INFO: 一般的な情報")
    logger.warning("WARNING: 警告メッセージ")
    logger.error("ERROR: エラーメッセージ")
    logger.critical("CRITICAL: 重大なエラーメッセージ")

    return {
        "message": "各ログレベルのデモが実行されました",
        "levels": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    }
