"""
ヘルスチェックエンドポイントのテスト

ヘルスチェック機能の動作を確認するテストケースを実装します。
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.health
class TestHealthCheck:
    """ヘルスチェックエンドポイントのテスト"""

    def test_basic_health_check(self):
        """基本的なヘルスチェックテスト"""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "api_version" in data
        assert "timestamp" in data
        assert "environment" in data

    def test_detailed_health_check(self):
        """詳細なヘルスチェックテスト"""
        response = client.get("/health/detailed")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 基本情報の確認
        assert "status" in data
        assert "version" in data
        assert "api_version" in data
        assert "timestamp" in data
        assert "environment" in data
        assert "checks" in data
        assert "response_time_ms" in data

        # 各チェック項目の確認
        checks = data["checks"]
        assert "database" in checks
        assert "authentication" in checks
        assert "environment" in checks

        # データベースチェック
        db_check = checks["database"]
        assert "status" in db_check
        assert "response_time_ms" in db_check
        assert "connection" in db_check

        # 認証システムチェック
        auth_check = checks["authentication"]
        assert "status" in auth_check
        assert "response_time_ms" in auth_check
        assert "api_key_configured" in auth_check
        assert "secret_key_configured" in auth_check
        assert "auth_types" in auth_check

        # 環境変数チェック
        env_check = checks["environment"]
        assert "status" in env_check
        assert "missing_variables" in env_check
        assert "environment" in env_check
        assert "debug_mode" in env_check

    def test_readiness_check(self):
        """Readiness Probeテスト"""
        response = client.get("/health/ready")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "status" in data
        assert data["status"] == "ready"
        assert "timestamp" in data
        assert "checks" in data

        checks = data["checks"]
        assert "database" in checks
        assert "environment" in checks

    def test_liveness_check(self):
        """Liveness Probeテスト"""
        response = client.get("/health/live")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "status" in data
        assert data["status"] == "alive"
        assert "timestamp" in data
        assert "uptime" in data

    def test_auth_health_check(self):
        """認証システムヘルスチェックテスト"""
        response = client.get("/health/auth")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "auth_systems" in data
        assert "supported_auth_types" in data
        assert "environment" in data

        auth_systems = data["auth_systems"]
        assert "api_key" in auth_systems
        assert "jwt" in auth_systems

        # APIキー設定の確認
        api_key_check = auth_systems["api_key"]
        assert "status" in api_key_check
        assert "key_length" in api_key_check

        # JWT設定の確認
        jwt_check = auth_systems["jwt"]
        assert "status" in jwt_check
        assert "algorithm" in jwt_check

    def test_simple_health_check(self):
        """シンプルなヘルスチェックテスト"""
        response = client.get("/health/simple")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "status" in data
        assert data["status"] == "ok"
        assert "timestamp" in data

        # タイムスタンプ形式の確認
        timestamp = data["timestamp"]
        assert "T" in timestamp
        assert "Z" in timestamp or "+" in timestamp


@pytest.mark.health
class TestHealthCheckEdgeCases:
    """ヘルスチェックエッジケースのテスト"""

    def test_health_check_response_time(self):
        """ヘルスチェックの応答時間テスト"""
        response = client.get("/health/detailed")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 応答時間が合理的な範囲内であることを確認
        response_time = data["response_time_ms"]
        assert response_time > 0
        assert response_time < 5000  # 5秒以内

    def test_health_check_timestamp_format(self):
        """タイムスタンプ形式のテスト"""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # ISO 8601形式のタイムスタンプであることを確認
        timestamp = data["timestamp"]
        assert "T" in timestamp
        assert "Z" in timestamp or "+" in timestamp

    def test_health_check_environment_variables(self):
        """環境変数チェックのテスト"""
        response = client.get("/health/detailed")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        env_check = data["checks"]["environment"]

        # 環境変数の確認
        assert "environment" in env_check
        assert "debug_mode" in env_check
        assert "missing_variables" in env_check

        # missing_variablesがリストであることを確認
        missing_vars = env_check["missing_variables"]
        assert isinstance(missing_vars, list)

    def test_health_check_database_connection(self):
        """データベース接続チェックのテスト"""
        response = client.get("/health/detailed")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        db_check = data["checks"]["database"]

        # データベースチェックの構造確認
        assert "status" in db_check
        assert "response_time_ms" in db_check
        assert "connection" in db_check

        # 応答時間が合理的であることを確認
        response_time = db_check["response_time_ms"]
        assert response_time > 0
        assert response_time < 1000  # 1秒以内

    def test_health_check_authentication_config(self):
        """認証設定チェックのテスト"""
        response = client.get("/health/detailed")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        auth_check = data["checks"]["authentication"]

        # 認証チェックの構造確認
        assert "status" in auth_check
        assert "response_time_ms" in auth_check
        assert "api_key_configured" in auth_check
        assert "secret_key_configured" in auth_check
        assert "auth_types" in auth_check

        # 認証タイプの確認
        auth_types = auth_check["auth_types"]
        assert "api_key" in auth_types
        assert "jwt" in auth_types


@pytest.mark.health
class TestHealthCheckIntegration:
    """ヘルスチェック統合テスト"""

    def test_all_health_endpoints(self):
        """全てのヘルスチェックエンドポイントのテスト"""
        endpoints = ["/health", "/health/detailed", "/health/ready", "/health/live", "/health/auth"]

        for endpoint in endpoints:
            response = client.get(endpoint)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # 全てのエンドポイントでタイムスタンプが含まれていることを確認
            assert "timestamp" in data

    def test_health_check_consistency(self):
        """ヘルスチェックの一貫性テスト"""
        # 複数回のリクエストで一貫性を確認
        responses = []
        for _ in range(3):
            response = client.get("/health")
            responses.append(response.json())

        # 基本情報が一貫していることを確認
        for data in responses:
            assert data["status"] == "healthy"
            assert "version" in data
            assert "api_version" in data
            assert "timestamp" in data

    def test_health_check_error_handling(self):
        """ヘルスチェックエラーハンドリングテスト"""
        # 存在しないエンドポイントへのリクエスト
        response = client.get("/health/nonexistent")

        assert response.status_code == status.HTTP_404_NOT_FOUND
