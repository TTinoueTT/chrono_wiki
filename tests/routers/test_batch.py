"""
バッチ処理エンドポイントのテスト

APIキー認証専用のバッチ処理エンドポイントのテストを実装します。
"""

import os

import pytest
from dotenv import load_dotenv
from fastapi import status


@pytest.fixture(scope="session")
def api_key():
    # fixture実行時に必ず.envをロード
    load_dotenv(override=True)
    key = os.getenv("API_KEY")
    if key is None:
        raise RuntimeError("API_KEY is not set in environment variables or .env")
    return key


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app)


@pytest.mark.batch
class TestBatchEndpoints:
    """バッチ処理エンドポイントのテスト"""

    def test_batch_get_persons(self, client, api_key):
        """バッチ人物取得テスト"""
        headers = {"X-API-Key": api_key}
        response = client.get("/api/v1/batch/persons/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_batch_get_events(self, client, api_key):
        """バッチイベント取得テスト"""
        headers = {"X-API-Key": api_key}
        response = client.get("/api/v1/batch/events/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_batch_get_tags(self, client, api_key):
        """バッチタグ取得テスト"""
        headers = {"X-API-Key": api_key}
        response = client.get("/api/v1/batch/tags/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_batch_get_persons_with_limit(self, client, api_key):
        """バッチ人物取得（制限付き）テスト"""
        headers = {"X-API-Key": api_key}
        response = client.get("/api/v1/batch/persons/?limit=10", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_batch_get_persons_with_skip(self, client, api_key):
        """バッチ人物取得（スキップ付き）テスト"""
        headers = {"X-API-Key": api_key}
        response = client.get("/api/v1/batch/persons/?skip=5&limit=10", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_batch_stats(self, client, api_key):
        """バッチ統計情報取得テスト"""
        headers = {"X-API-Key": api_key}
        response = client.get("/api/v1/batch/stats", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "persons" in data
        assert "events" in data
        assert "tags" in data
        assert "total" in data
        assert isinstance(data["persons"], int)
        assert isinstance(data["events"], int)
        assert isinstance(data["tags"], int)
        assert isinstance(data["total"], int)


@pytest.mark.batch
class TestBatchAuth:
    """バッチ処理認証テスト"""

    def test_batch_endpoints_require_api_key(self, client):
        """バッチエンドポイントはAPIキー認証が必要"""
        # APIキーなし
        response = client.get("/api/v1/batch/persons/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # 無効なAPIキー
        response = client.get("/api/v1/batch/persons/", headers={"X-API-Key": "invalid"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_batch_endpoints_with_valid_api_key(self, client, api_key):
        """有効なAPIキーでのバッチエンドポイントアクセス"""
        headers = {"X-API-Key": api_key}
        response = client.get("/api/v1/batch/persons/", headers=headers)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.batch
class TestBatchLimits:
    """バッチ処理制限テスト"""

    def test_batch_get_persons_limit_enforcement(self, client, api_key):
        """バッチ人物取得の制限テスト"""
        headers = {"X-API-Key": api_key}
        # 制限を超えるリクエスト
        response = client.get("/api/v1/batch/persons/?limit=2000", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # 制限が1000に調整されることを確認
        assert len(data) <= 1000

    def test_batch_create_persons_limit(self, client, api_key):
        """バッチ人物作成の制限テスト"""
        headers = {"X-API-Key": api_key}
        # 制限を超えるバッチサイズ（100個を超える150個）
        persons = [
            {
                "ssid": f"test_person_{i}",
                "full_name": f"Test Person {i}",
                "display_name": f"Test{i}",
                "birth_date": "1900-01-01",
                "born_country": "Japan",
            }
            for i in range(150)
        ]
        response = client.post("/api/v1/batch/persons/", headers=headers, json=persons)
        # バッチサイズ制限により400エラーが返される
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Batch size cannot exceed 100 items" in response.json()["detail"]

    def test_batch_create_events_limit(self, client, api_key):
        """バッチイベント作成の制限テスト"""
        headers = {"X-API-Key": api_key}
        # 制限を超えるバッチサイズ（100個を超える150個）
        events = [
            {
                "ssid": f"test_event_{i}",
                "title": f"Test Event {i}",
                "description": f"Test event {i}",
                "start_date": "1900-01-01",
                "end_date": "1900-12-31",
                "location_name": "Japan",
            }
            for i in range(150)
        ]
        response = client.post("/api/v1/batch/events/", headers=headers, json=events)
        # バッチサイズ制限により400エラーが返される
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Batch size cannot exceed 100 items" in response.json()["detail"]


@pytest.mark.batch
class TestBatchPerformance:
    """バッチ処理パフォーマンステスト"""

    def test_batch_get_persons_performance(self, client, api_key):
        """バッチ人物取得のパフォーマンステスト"""
        import time

        headers = {"X-API-Key": api_key}
        start_time = time.time()
        response = client.get("/api/v1/batch/persons/?limit=100", headers=headers)
        end_time = time.time()

        assert response.status_code == status.HTTP_200_OK
        # バッチ処理は高速であることを確認（500ms以内）
        assert (end_time - start_time) < 0.5

    def test_batch_stats_performance(self, client, api_key):
        """バッチ統計情報取得のパフォーマンステスト"""
        import time

        headers = {"X-API-Key": api_key}
        start_time = time.time()
        response = client.get("/api/v1/batch/stats", headers=headers)
        end_time = time.time()

        assert response.status_code == status.HTTP_200_OK
        # 統計情報取得は高速であることを確認（200ms以内）
        assert (end_time - start_time) < 0.2
