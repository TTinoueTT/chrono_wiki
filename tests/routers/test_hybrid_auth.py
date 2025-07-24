"""
ハイブリッド認証システムのテスト

APIキー認証とJWT認証の統合テストを実装します。
"""

import os
import uuid

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


@pytest.mark.hybrid_auth
class TestHybridAuthMiddleware:
    """ハイブリッド認証ミドルウェアのテスト"""

    def test_api_key_auth_success(self, client, api_key):
        """APIキー認証成功テスト"""
        headers = {"X-API-Key": api_key}
        response = client.get("/api/v1/persons/", headers=headers)
        assert response.status_code == status.HTTP_200_OK

    def test_api_key_auth_failure(self, client, api_key):
        """APIキー認証失敗テスト"""
        response = client.get("/api/v1/persons/", headers={"X-API-Key": "invalid_key"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_jwt_auth_success(self, client):
        """JWT認証成功テスト"""
        # 1. ユーザー登録
        user_data = {
            "email": f"test_{uuid.uuid4()}@example.com",
            "username": f"testuser_{uuid.uuid4()}",
            "password": "testpassword123",
            "full_name": "JWT Test User",
        }
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # 2. ログインしてJWTトークン取得（登録したメールアドレスを使用）
        login_data = {"username": user_data["email"], "password": "testpassword123"}
        login_response = client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token_data = login_response.json()
        access_token = token_data["access_token"]

        # 3. JWTトークンでリソースアクセス
        jwt_headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/persons/", headers=jwt_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_no_auth_failure(self, client):
        """認証なしの失敗テスト"""
        response = client.get("/api/v1/persons/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_health_endpoint_no_auth(self, client):
        """ヘルスチェックエンドポイントは認証不要"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK

    def test_auth_endpoint_no_auth(self, client):
        """認証エンドポイントは認証不要"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]


@pytest.mark.hybrid_auth
class TestAuthDependencies:
    """認証依存性のテスト"""

    def test_require_auth_with_api_key(self, client, api_key):
        """APIキーでの認証要求テスト"""
        headers = {"X-API-Key": api_key}
        response = client.get("/api/v1/persons/", headers=headers)
        assert response.status_code == status.HTTP_200_OK

    def test_require_auth_with_jwt(self, client):
        """JWTでの認証要求テスト"""
        # 1. ユーザー登録
        user_data = {
            "email": f"test_{uuid.uuid4()}@example.com",
            "username": f"testuser_{uuid.uuid4()}",
            "password": "testpassword123",
            "full_name": "JWT Auth Test User",
        }
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # 2. ログインしてJWTトークン取得（登録したメールアドレスを使用）
        login_data = {"username": user_data["email"], "password": "testpassword123"}
        login_response = client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token_data = login_response.json()
        access_token = token_data["access_token"]

        # 3. JWTトークンでリソースアクセス
        jwt_headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/persons/", headers=jwt_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_require_auth_failure(self, client):
        """認証要求失敗テスト"""
        response = client.get("/api/v1/persons/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.hybrid_auth
class TestPermissionSystem:
    """権限システムのテスト"""

    def test_admin_access_with_api_key(self, client, api_key):
        """APIキーでの管理者権限アクセステスト"""
        # APIキー認証は管理者権限として扱われる
        headers = {"X-API-Key": api_key}
        response = client.get("/api/v1/users/", headers=headers)
        assert response.status_code == status.HTTP_200_OK

    def test_moderator_access_with_api_key(self, client, api_key):
        """APIキーでのモデレーター権限アクセステスト"""
        # APIキー認証は管理者権限として扱われる
        headers = {"X-API-Key": api_key}
        response = client.post(
            "/api/v1/persons/",
            headers=headers,
            json={
                "ssid": f"test_person_{uuid.uuid4()}",
                "full_name": "Test Person",
                "display_name": "Test",
                "birth_date": "1900-01-01",
                "born_country": "Japan",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_user_access_with_jwt(self, client):
        """JWTでの一般ユーザー権限アクセステスト"""
        # 1. 一般ユーザー登録
        user_data = {
            "email": f"test_{uuid.uuid4()}@example.com",
            "username": f"testuser_{uuid.uuid4()}",
            "password": "testpassword123",
            "full_name": "User Test User",
        }
        client.post("/api/v1/auth/register", json=user_data)

        # 2. ログインしてJWTトークン取得（登録したメールアドレスを使用）
        login_data = {"username": user_data["email"], "password": "testpassword123"}
        login_response = client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token_data = login_response.json()
        access_token = token_data["access_token"]

        # 3. JWTトークンで閲覧操作（成功）
        jwt_headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/persons/", headers=jwt_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_moderator_access_with_jwt(self, client):
        """JWTでのモデレーター権限アクセステスト"""
        # 1. モデレーター権限ユーザー登録
        user_data = {
            "email": f"test_{uuid.uuid4()}@example.com",
            "username": f"testuser_{uuid.uuid4()}",
            "password": "testpassword123",
            "full_name": "Moderator Test User",
            "role": "moderator",
        }
        client.post("/api/v1/auth/register", json=user_data)

        # 2. ログインしてJWTトークン取得（登録したメールアドレスを使用）
        login_data = {"username": user_data["email"], "password": "testpassword123"}
        login_response = client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token_data = login_response.json()
        access_token = token_data["access_token"]

        # 3. JWTトークンで編集操作（成功）
        jwt_headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post(
            "/api/v1/persons/",
            headers=jwt_headers,
            json={
                "ssid": f"test_person_{uuid.uuid4()}",
                "full_name": "Moderator Test Person",
                "display_name": "Test",
                "birth_date": "1900-01-01",
                "born_country": "Japan",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.hybrid_auth
class TestAuthPerformance:
    """認証パフォーマンスのテスト"""

    def test_api_key_auth_speed(self, client, api_key):
        """APIキー認証の速度テスト"""
        import time

        headers = {"X-API-Key": api_key}
        start_time = time.time()
        response = client.get("/api/v1/persons/", headers=headers)
        end_time = time.time()

        assert response.status_code == status.HTTP_200_OK
        # APIキー認証は高速であることを確認（100ms以内）
        assert (end_time - start_time) < 0.1

    def test_jwt_auth_speed(self, client):
        """JWT認証の速度テスト"""
        import time

        # 1. ユーザー登録
        user_data = {
            "email": f"test_{uuid.uuid4()}@example.com",
            "username": f"testuser_{uuid.uuid4()}",
            "password": "testpassword123",
            "full_name": "Speed Test User",
        }
        client.post("/api/v1/auth/register", json=user_data)

        # 2. ログインしてJWTトークン取得（登録したメールアドレスを使用）
        login_data = {"username": user_data["email"], "password": "testpassword123"}
        login_response = client.post("/api/v1/auth/login", data=login_data)
        token_data = login_response.json()
        access_token = token_data["access_token"]

        # 3. JWTトークンでの速度テスト
        jwt_headers = {"Authorization": f"Bearer {access_token}"}
        start_time = time.time()
        response = client.get("/api/v1/persons/", headers=jwt_headers)
        end_time = time.time()

        assert response.status_code == status.HTTP_200_OK
        # JWT認証はAPIキー認証より若干遅いが、許容範囲内
        assert (end_time - start_time) < 0.5


@pytest.mark.hybrid_auth
class TestAuthIntegration:
    """認証統合テスト"""

    def test_mixed_auth_requests(self, client, api_key):
        """混合認証リクエストのテスト"""
        # APIキー認証
        headers1 = {"X-API-Key": api_key}
        response1 = client.get("/api/v1/persons/", headers=headers1)
        assert response1.status_code == status.HTTP_200_OK

        # JWT認証
        # 1. ユーザー登録
        user_data = {
            "email": f"test_{uuid.uuid4()}@example.com",
            "username": f"testuser_{uuid.uuid4()}",
            "password": "testpassword123",
            "full_name": "Mixed Test User",
        }
        client.post("/api/v1/auth/register", json=user_data)

        # 2. ログインしてJWTトークン取得（登録したメールアドレスを使用）
        login_data = {"username": user_data["email"], "password": "testpassword123"}
        login_response = client.post("/api/v1/auth/login", data=login_data)
        token_data = login_response.json()
        access_token = token_data["access_token"]

        # 3. JWTトークンでリソースアクセス
        headers2 = {"Authorization": f"Bearer {access_token}"}
        response2 = client.get("/api/v1/persons/", headers=headers2)
        assert response2.status_code == status.HTTP_200_OK

        # 認証なし
        response3 = client.get("/api/v1/persons/")
        assert response3.status_code == status.HTTP_401_UNAUTHORIZED

    def test_auth_priority(self, client, api_key):
        """認証優先順位のテスト"""
        # 1. ユーザー登録・ログイン
        user_data = {
            "email": f"test_{uuid.uuid4()}@example.com",
            "username": f"testuser_{uuid.uuid4()}",
            "password": "testpassword123",
            "full_name": "Priority Test User",
        }
        client.post("/api/v1/auth/register", json=user_data)

        login_data = {"username": user_data["email"], "password": "testpassword123"}
        login_response = client.post("/api/v1/auth/login", data=login_data)
        token_data = login_response.json()
        access_token = token_data["access_token"]

        # APIキーとJWTの両方を送信した場合、APIキーが優先される
        headers = {"X-API-Key": api_key, "Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/persons/", headers=headers)
        assert response.status_code == status.HTTP_200_OK

    def test_complete_auth_flow(self, client, api_key):
        """完全な認証フローテスト"""
        # 1. ユーザー登録
        user_data = {
            "email": f"test_{uuid.uuid4()}@example.com",
            "username": f"testuser_{uuid.uuid4()}",
            "password": "testpassword123",
            "full_name": "Flow Test User",
        }
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # 2. ログインしてJWTトークン取得（登録したメールアドレスを使用）
        login_data = {"username": user_data["email"], "password": "testpassword123"}
        login_response = client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token_data = login_response.json()
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]

        # 3. JWTトークンでリソース操作
        jwt_headers = {"Authorization": f"Bearer {access_token}"}

        # 閲覧操作（一般ユーザーでも可能）
        response = client.get("/api/v1/persons/", headers=jwt_headers)
        assert response.status_code == status.HTTP_200_OK

        # 編集操作（一般ユーザーは権限不足で403）
        response = client.post(
            "/api/v1/persons/",
            headers=jwt_headers,
            json={
                "ssid": f"test_person_{uuid.uuid4()}",
                "full_name": "Flow Test Person",
                "display_name": "Test",
                "birth_date": "1900-01-01",
                "born_country": "Japan",
            },
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # 4. トークン更新
        refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh_response.status_code == status.HTTP_200_OK

        new_token_data = refresh_response.json()
        new_access_token = new_token_data["access_token"]

        # 5. 新しいトークンでリソース操作（閲覧のみ）
        new_jwt_headers = {"Authorization": f"Bearer {new_access_token}"}
        response = client.get("/api/v1/persons/", headers=new_jwt_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_moderator_auth_flow(self, client, api_key):
        """モデレーター権限での認証フローテスト"""
        # 1. モデレーター権限ユーザー登録
        user_data = {
            "email": f"test_{uuid.uuid4()}@example.com",
            "username": f"testuser_{uuid.uuid4()}",
            "password": "testpassword123",
            "full_name": "Moderator Flow User",
            "role": "moderator",
        }
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # 2. ログインしてJWTトークン取得（登録したメールアドレスを使用）
        login_data = {"username": user_data["email"], "password": "testpassword123"}
        login_response = client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token_data = login_response.json()
        access_token = token_data["access_token"]

        # 3. JWTトークンでリソース操作
        jwt_headers = {"Authorization": f"Bearer {access_token}"}

        # 閲覧操作（モデレーターでも可能）
        response = client.get("/api/v1/persons/", headers=jwt_headers)
        assert response.status_code == status.HTTP_200_OK

        # 編集操作（モデレーターは可能）
        response = client.post(
            "/api/v1/persons/",
            headers=jwt_headers,
            json={
                "ssid": f"test_person_{uuid.uuid4()}",
                "full_name": "Moderator Test Person",
                "display_name": "Test",
                "birth_date": "1900-01-01",
                "born_country": "Japan",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
