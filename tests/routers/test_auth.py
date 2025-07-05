"""
認証ルーターのテスト

auth.pyのカバレッジを向上させるための包括的なテストケースを実装します。
"""

import pytest
from fastapi import status

from tests.routers.fixtures.user_data import UserTestData, UserTestScenarios


@pytest.mark.router
@pytest.mark.integration
class TestAuthErrorScenarios:
    """認証エラーシナリオのテスト"""

    def test_login_account_locked(self, auth_client):
        """アカウントロック時のログインテスト"""
        # ユーザーを登録
        user_data = UserTestData.create_user_data(
            email="locked@example.com", username="lockeduser", full_name="Locked User"
        )
        auth_client.post("/auth/register", json=user_data)

        # 5回間違ったパスワードでログインしてアカウントをロック
        for i in range(5):
            login_data = {
                "username": "locked@example.com",
                "password": "wrongpassword",
            }
            response = auth_client.post("/auth/login", data=login_data)
            if i < 4:  # 最初の4回は401
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
            else:  # 5回目は423（ロック）
                assert response.status_code == status.HTTP_423_LOCKED

        # 正しいパスワードでもロックされているためログインできない
        correct_login_data = {
            "username": "locked@example.com",
            "password": "testpassword123",
        }
        response = auth_client.post("/auth/login", data=correct_login_data)
        assert response.status_code == status.HTTP_423_LOCKED

    def test_refresh_token_invalid_token(self, auth_client):
        """無効なリフレッシュトークンのテスト"""
        response = auth_client.post("/auth/refresh", json={"refresh_token": "invalid_token"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_wrong_type(self, auth_client):
        """間違ったタイプのトークンでのリフレッシュテスト"""
        # ユーザーを登録してログイン
        user_data = UserTestData.create_user_data(
            email="refresh@example.com", username="refreshuser", full_name="Refresh User"
        )
        auth_client.post("/auth/register", json=user_data)

        login_data = {
            "username": "refresh@example.com",
            "password": "testpassword123",
        }
        login_response = auth_client.post("/auth/login", data=login_data)
        access_token = login_response.json()["access_token"]

        # アクセストークンをリフレッシュトークンとして使用
        response = auth_client.post("/auth/refresh", json={"refresh_token": access_token})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_inactive_user(self, auth_client):
        """非アクティブユーザーのリフレッシュトークンテスト"""
        # ユーザーを登録してログイン
        user_data = UserTestData.create_user_data(
            email="inactive@example.com", username="inactiveuser", full_name="Inactive User"
        )
        register_response = auth_client.post("/auth/register", json=user_data)
        user_id = register_response.json()["id"]

        login_data = {
            "username": "inactive@example.com",
            "password": "testpassword123",
        }
        login_response = auth_client.post("/auth/login", data=login_data)
        refresh_token = login_response.json()["refresh_token"]

        # 管理者としてログインしてユーザーを無効化
        admin_data = UserTestData.create_admin_data()
        auth_client.post("/auth/register", json=admin_data)

        admin_login_data = {
            "username": admin_data["email"],
            "password": admin_data["password"],
        }
        admin_login_response = auth_client.post("/auth/login", data=admin_login_data)
        admin_token = admin_login_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # ユーザーを無効化
        auth_client.post(f"/users/{user_id}/deactivate", headers=admin_headers)

        # 無効化されたユーザーのリフレッシュトークンを使用
        response = auth_client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_with_missing_sub(self, auth_client):
        """subフィールドが欠けているリフレッシュトークンのテスト"""
        response = auth_client.post("/auth/refresh", json={"refresh_token": "invalid_token_missing_sub"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_with_none_sub(self, auth_client):
        """subフィールドがNoneのリフレッシュトークンのテスト"""
        response = auth_client.post("/auth/refresh", json={"refresh_token": "invalid_token_none_sub"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.router
@pytest.mark.integration
class TestAuthEdgeCases:
    """認証エッジケースのテスト"""

    def test_failed_login_attempts_increment(self, auth_client):
        """ログイン失敗回数の増加テスト"""
        # ユーザーを登録
        user_data = UserTestData.create_user_data(
            email="failed@example.com", username="faileduser", full_name="Failed User"
        )
        auth_client.post("/auth/register", json=user_data)

        # 3回間違ったパスワードでログイン
        for i in range(3):
            login_data = {
                "username": "failed@example.com",
                "password": "wrongpassword",
            }
            response = auth_client.post("/auth/login", data=login_data)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # 正しいパスワードでログイン（まだロックされていない）
        correct_login_data = {
            "username": "failed@example.com",
            "password": "testpassword123",
        }
        response = auth_client.post("/auth/login", data=correct_login_data)
        assert response.status_code == status.HTTP_200_OK

    def test_successful_login_resets_failed_attempts(self, auth_client):
        """成功したログインで失敗回数がリセットされるテスト"""
        # ユーザーを登録
        user_data = UserTestData.create_user_data(
            email="reset@example.com", username="resetuser", full_name="Reset User"
        )
        auth_client.post("/auth/register", json=user_data)

        # 2回間違ったパスワードでログイン
        for _ in range(2):
            login_data = {
                "username": "reset@example.com",
                "password": "wrongpassword",
            }
            auth_client.post("/auth/login", data=login_data)

        # 正しいパスワードでログイン
        correct_login_data = {
            "username": "reset@example.com",
            "password": "testpassword123",
        }
        response = auth_client.post("/auth/login", data=correct_login_data)
        assert response.status_code == status.HTTP_200_OK

        # 再度間違ったパスワードでログイン（失敗回数がリセットされているため1回目）
        wrong_login_data = {
            "username": "reset@example.com",
            "password": "wrongpassword",
        }
        response = auth_client.post("/auth/login", data=wrong_login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_register_with_invalid_data(self, auth_client):
        """無効なデータでのユーザー登録テスト"""
        # 無効なメールアドレスで登録を試行
        invalid_user_data = {
            "email": "invalid-email",
            "username": "invaliduser",
            "password": "password123",
            "full_name": "Invalid User",
        }
        response = auth_client.post("/auth/register", json=invalid_user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_user_with_invalid_data(self, auth_client):
        """無効なデータでのユーザー更新テスト"""
        # ユーザーを登録してログイン
        user_data = UserTestData.create_user_data(
            email="update@example.com", username="updateuser", full_name="Update User"
        )
        auth_client.post("/auth/register", json=user_data)

        login_data = {
            "username": "update@example.com",
            "password": "testpassword123",
        }
        login_response = auth_client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 無効なメールアドレスで更新を試行
        invalid_update_data = {
            "email": "invalid-email",
        }
        response = auth_client.put("/auth/me", json=invalid_update_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.router
@pytest.mark.integration
class TestAuthSuccessScenarios:
    """認証成功シナリオのテスト"""

    def test_successful_user_registration(self, auth_client):
        """正常なユーザー登録テスト"""
        user_data = UserTestData.create_user_data(
            email="success@example.com", username="successuser", full_name="Success User"
        )
        response = auth_client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "success@example.com"
        assert data["username"] == "successuser"
        assert "password" not in data

    def test_successful_login(self, auth_client):
        """正常なログインテスト"""
        # ユーザーを登録
        user_data = UserTestData.create_user_data(
            email="login@example.com", username="loginuser", full_name="Login User"
        )
        auth_client.post("/auth/register", json=user_data)

        # ログイン
        login_data = {
            "username": "login@example.com",
            "password": "testpassword123",
        }
        response = auth_client.post("/auth/login", data=login_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_successful_token_refresh(self, auth_client):
        """正常なトークン更新テスト"""
        # ユーザーを登録してログイン
        user_data = UserTestData.create_user_data(
            email="refresh@example.com", username="refreshuser", full_name="Refresh User"
        )
        auth_client.post("/auth/register", json=user_data)

        login_data = {
            "username": "refresh@example.com",
            "password": "testpassword123",
        }
        login_response = auth_client.post("/auth/login", data=login_data)
        refresh_token = login_response.json()["refresh_token"]

        # トークンを更新
        response = auth_client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_successful_user_update(self, auth_client):
        """正常なユーザー情報更新テスト"""
        # ユーザーを登録してログイン
        user_data = UserTestData.create_user_data(
            email="update@example.com", username="updateuser", full_name="Update User"
        )
        auth_client.post("/auth/register", json=user_data)

        login_data = {
            "username": "update@example.com",
            "password": "testpassword123",
        }
        login_response = auth_client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # ユーザー情報を更新
        update_data = {
            "full_name": "Updated Name",
            "bio": "Updated bio",
        }
        response = auth_client.put("/auth/me", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["bio"] == "Updated bio"

    def test_successful_password_change(self, auth_client):
        """正常なパスワード変更テスト"""
        # ユーザーを登録してログイン
        user_data = UserTestData.create_user_data(
            email="changepass@example.com", username="changepassuser", full_name="Change Pass User"
        )
        auth_client.post("/auth/register", json=user_data)

        login_data = {
            "username": "changepass@example.com",
            "password": "testpassword123",
        }
        login_response = auth_client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # パスワードを変更
        response = auth_client.post(
            "/auth/change-password",
            params={"current_password": "testpassword123", "new_password": "newpassword123"},
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK

        # 新しいパスワードでログイン
        new_login_data = {
            "username": "changepass@example.com",
            "password": "newpassword123",
        }
        new_login_response = auth_client.post("/auth/login", data=new_login_data)
        assert new_login_response.status_code == status.HTTP_200_OK

    def test_successful_logout(self, auth_client):
        """正常なログアウトテスト"""
        # ユーザーを登録してログイン
        user_data = UserTestData.create_user_data(
            email="logout@example.com", username="logoutuser", full_name="Logout User"
        )
        auth_client.post("/auth/register", json=user_data)

        login_data = {
            "username": "logout@example.com",
            "password": "testpassword123",
        }
        login_response = auth_client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # ログアウト
        response = auth_client.post("/auth/logout", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Logged out successfully"

    def test_get_current_user_info(self, auth_client):
        """現在のユーザー情報取得テスト"""
        # ユーザーを登録してログイン
        user_data = UserTestData.create_user_data(email="me@example.com", username="meuser", full_name="Me User")
        auth_client.post("/auth/register", json=user_data)

        login_data = {
            "username": "me@example.com",
            "password": "testpassword123",
        }
        login_response = auth_client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 現在のユーザー情報を取得
        response = auth_client.get("/auth/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "me@example.com"
        assert data["username"] == "meuser"
        assert data["full_name"] == "Me User"


@pytest.mark.router
@pytest.mark.integration
class TestAuthParameterizedScenarios:
    """パラメータ化認証シナリオのテスト"""

    @pytest.mark.parametrize(
        "scenario",
        UserTestScenarios.registration_scenarios(),
        ids=[s["name"] for s in UserTestScenarios.registration_scenarios()],
    )
    def test_user_registration_scenarios(self, auth_client, scenario):
        """ユーザー登録の様々なシナリオをテスト"""
        # 重複チェックテストの場合は、最初にユーザーを作成
        if scenario["name"] in ["duplicate_email", "duplicate_username"]:
            # 重複チェック用の最初のユーザーを作成
            first_user_data = UserTestData.create_user_data(
                email="duplicate@example.com" if scenario["name"] == "duplicate_email" else "different@example.com",
                username="differentuser" if scenario["name"] == "duplicate_email" else "duplicateuser",
                full_name="First User",
            )
            first_response = auth_client.post("/auth/register", json=first_user_data)
            assert first_response.status_code == status.HTTP_201_CREATED

        response = auth_client.post("/auth/register", json=scenario["data"])

        assert response.status_code == scenario["expected_status"]

        if scenario["expected_status"] == status.HTTP_201_CREATED:
            data = response.json()
            assert data["email"] == scenario["data"]["email"]
            assert data["username"] == scenario["data"]["username"]
            assert "password" not in data

    @pytest.fixture(autouse=True)
    def setup_user(self, auth_client):
        """テスト用ユーザーをセットアップ"""
        user_data = UserTestData.create_user_data(email="test@example.com", username="testuser", full_name="Test User")
        auth_client.post("/auth/register", json=user_data)

    @pytest.mark.parametrize(
        "scenario", UserTestScenarios.login_scenarios(), ids=[s["name"] for s in UserTestScenarios.login_scenarios()]
    )
    def test_user_login_scenarios(self, auth_client, scenario):
        """ログインの様々なシナリオをテスト"""
        response = auth_client.post("/auth/login", data=scenario["login_data"])

        assert response.status_code == scenario["expected_status"]

        if scenario["expected_status"] == status.HTTP_200_OK:
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"


@pytest.mark.router
@pytest.mark.integration
class TestAuthPasswordChangeScenarios:
    """パラメータ化パスワード変更テスト"""

    @pytest.fixture(autouse=True)
    def setup_authenticated_user(self, auth_client):
        """認証済みユーザーをセットアップ"""
        # ユーザー登録
        user_data = UserTestData.create_user_data(
            email="password@example.com", username="passworduser", full_name="Password User"
        )
        auth_client.post("/auth/register", json=user_data)

        # ログイン
        login_data = {"username": "password@example.com", "password": "testpassword123"}
        login_response = auth_client.post("/auth/login", data=login_data)
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @pytest.mark.parametrize(
        "scenario",
        UserTestScenarios.password_change_scenarios(),
        ids=[s["name"] for s in UserTestScenarios.password_change_scenarios()],
    )
    def test_password_change_scenarios(self, auth_client, scenario):
        """パスワード変更の様々なシナリオをテスト"""
        response = auth_client.post(
            "/auth/change-password",
            params={"current_password": scenario["current_password"], "new_password": scenario["new_password"]},
            headers=self.headers,
        )

        assert response.status_code == scenario["expected_status"]
