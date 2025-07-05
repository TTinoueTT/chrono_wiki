"""
ユーザールーターの結合テスト

ユーザーエンドポイントの統合テストを実装します。
実際のデータベースとサービスを使用してテストします。
"""

import pytest
from fastapi import status

from tests.routers.fixtures.user_data import UserTestScenarios


@pytest.mark.router
@pytest.mark.integration
class TestUserManagement:
    """ユーザー管理系テスト（管理者権限）"""

    def test_user_management_as_admin(self, auth_client, sample_user_data, admin_user_data):
        """管理者としてのユーザー管理テスト"""
        # 一般ユーザーを作成
        register_response = auth_client.post("/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        user_id = register_response.json()["id"]

        # 管理者ユーザーを作成
        admin_register_response = auth_client.post("/auth/register", json=admin_user_data)
        assert admin_register_response.status_code == status.HTTP_201_CREATED

        # 管理者でログイン
        login_data = {
            "username": admin_user_data["email"],
            "password": admin_user_data["password"],
        }
        login_response = auth_client.post("/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # ユーザーを無効化
        deactivate_response = auth_client.post(f"/users/{user_id}/deactivate", headers=headers)
        assert deactivate_response.status_code == status.HTTP_200_OK
        assert deactivate_response.json()["is_active"] is False

        # ユーザーを有効化
        activate_response = auth_client.post(f"/users/{user_id}/activate", headers=headers)
        assert activate_response.status_code == status.HTTP_200_OK
        assert activate_response.json()["is_active"] is True


@pytest.mark.router
@pytest.mark.integration
class TestUserAnalytics:
    """ユーザー分析・統計系テスト（モデレーター権限）"""

    def test_user_stats_as_moderator(self, auth_client, moderator_user_data):
        """モデレーターとしてのユーザー統計取得テスト"""
        # モデレーターユーザーを作成
        register_response = auth_client.post("/auth/register", json=moderator_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        login_data = {
            "username": moderator_user_data["email"],
            "password": moderator_user_data["password"],
        }
        login_response = auth_client.post("/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 統計を取得
        response = auth_client.get("/users/stats/count", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_users" in data
        assert "active_users" in data
        assert "inactive_users" in data
        assert data["total_users"] >= 1
        assert data["active_users"] >= 1


@pytest.mark.router
@pytest.mark.integration
class TestUserWorkflow:
    """ユーザーワークフロー統合テスト"""

    def test_user_workflow_complete(self, auth_client, sample_user_data):
        """完全なユーザーワークフローテスト"""
        # 1. ユーザー登録
        register_response = auth_client.post("/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        user_id = register_response.json()["id"]

        # 2. ログイン
        login_data = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"],
        }
        login_response = auth_client.post("/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. ユーザー情報更新
        update_data = {
            "full_name": "Updated User",
            "bio": "Updated bio",
        }
        update_response = auth_client.put(f"/users/{user_id}", json=update_data, headers=headers)
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["full_name"] == "Updated User"

        # 4. パスワード変更
        change_password_response = auth_client.post(
            "/auth/change-password",
            params={
                "current_password": sample_user_data["password"],
                "new_password": "newpassword123",
            },
            headers=headers,
        )
        assert change_password_response.status_code == status.HTTP_200_OK

        # 5. 新しいパスワードでログイン
        new_login_data = {
            "username": sample_user_data["email"],
            "password": "newpassword123",
        }
        new_login_response = auth_client.post("/auth/login", data=new_login_data)
        assert new_login_response.status_code == status.HTTP_200_OK

        # 6. ログアウト
        logout_response = auth_client.post("/auth/logout", headers=headers)
        assert logout_response.status_code == status.HTTP_200_OK


@pytest.mark.router
@pytest.mark.integration
class TestUserRoleAccess:
    """ユーザー権限アクセステスト"""

    @pytest.mark.parametrize(
        "role,can_access_admin_endpoints", [("user", False), ("moderator", False), ("admin", True)]
    )
    def test_admin_endpoint_access(self, auth_client, role, can_access_admin_endpoints):
        """管理者エンドポイントへのアクセス権限テスト"""
        # 指定された役割のユーザーを作成
        user_data = {
            "email": f"{role}@example.com",
            "username": f"{role}user",
            "password": f"{role}password123",
            "full_name": f"{role.title()} User",
            "role": role,
        }
        auth_client.post("/auth/register", json=user_data)

        # ログイン
        login_response = auth_client.post(
            "/auth/login", data={"username": f"{role}@example.com", "password": f"{role}password123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 管理者エンドポイントにアクセス
        response = auth_client.get("/users/", headers=headers)

        if can_access_admin_endpoints:
            assert response.status_code == status.HTTP_200_OK
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        "role,can_access_moderator_endpoints", [("user", False), ("moderator", True), ("admin", True)]
    )
    def test_moderator_endpoint_access(self, auth_client, role, can_access_moderator_endpoints):
        """モデレーターエンドポイントへのアクセス権限テスト"""
        # 指定された役割のユーザーを作成
        user_data = {
            "email": f"{role}@example.com",
            "username": f"{role}user",
            "password": f"{role}password123",
            "full_name": f"{role.title()} User",
            "role": role,
        }
        auth_client.post("/auth/register", json=user_data)

        # ログイン
        login_response = auth_client.post(
            "/auth/login", data={"username": f"{role}@example.com", "password": f"{role}password123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # モデレーターエンドポイントにアクセス
        response = auth_client.get("/users/stats/count", headers=headers)

        if can_access_moderator_endpoints:
            assert response.status_code == status.HTTP_200_OK
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.router
@pytest.mark.integration
class TestUserRegistrationScenarios:
    """パラメータ化ユーザー登録テスト"""

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
            first_user_data = {
                "email": "duplicate@example.com" if scenario["name"] == "duplicate_email" else "different@example.com",
                "username": "differentuser" if scenario["name"] == "duplicate_email" else "duplicateuser",
                "password": "password123",
                "full_name": "First User",
                "role": "user",
            }
            first_response = auth_client.post("/auth/register", json=first_user_data)
            assert first_response.status_code == status.HTTP_201_CREATED

        response = auth_client.post("/auth/register", json=scenario["data"])

        assert response.status_code == scenario["expected_status"]

        if scenario["expected_status"] == status.HTTP_201_CREATED:
            data = response.json()
            assert data["email"] == scenario["data"]["email"]
            assert data["username"] == scenario["data"]["username"]
            assert "password" not in data


@pytest.mark.router
@pytest.mark.integration
class TestUserLoginScenarios:
    """パラメータ化ログインテスト"""

    @pytest.fixture(autouse=True)
    def setup_user(self, auth_client):
        """テスト用ユーザーをセットアップ"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "full_name": "Test User",
            "role": "user",
        }
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
class TestPasswordChangeScenarios:
    """パラメータ化パスワード変更テスト"""

    @pytest.fixture(autouse=True)
    def setup_authenticated_user(self, auth_client):
        """認証済みユーザーをセットアップ"""
        # ユーザー登録
        user_data = {
            "email": "password@example.com",
            "username": "passworduser",
            "password": "testpassword123",
            "full_name": "Password User",
            "role": "user",
        }
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


@pytest.mark.router
@pytest.mark.integration
class TestUserManagementScenarios:
    """パラメータ化ユーザー管理テスト"""

    @pytest.fixture(autouse=True)
    def setup_admin_and_user(self, auth_client):
        """管理者と一般ユーザーをセットアップ"""
        # 管理者ユーザーを作成
        admin_data = {
            "email": "admin@example.com",
            "username": "adminuser",
            "password": "adminpassword123",
            "full_name": "Admin User",
            "role": "admin",
        }
        admin_register = auth_client.post("/auth/register", json=admin_data)
        self.admin_user = admin_register.json()

        # 管理者でログイン
        admin_login = auth_client.post(
            "/auth/login", data={"username": "admin@example.com", "password": "adminpassword123"}
        )
        self.admin_token = admin_login.json()["access_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

        # 一般ユーザーを作成
        user_data = {
            "email": "user@example.com",
            "username": "normaluser",
            "password": "userpassword123",
            "full_name": "Normal User",
            "role": "user",
        }
        user_register = auth_client.post("/auth/register", json=user_data)
        self.normal_user = user_register.json()

    @pytest.mark.parametrize(
        "scenario",
        UserTestScenarios.user_management_scenarios(),
        ids=[s["name"] for s in UserTestScenarios.user_management_scenarios()],
    )
    def test_user_management_scenarios(self, auth_client, scenario):
        """ユーザー管理の様々なシナリオをテスト"""
        user_id = self.normal_user["id"]
        action = scenario["action"]

        if action == "activate":
            response = auth_client.post(f"/users/{user_id}/activate", headers=self.admin_headers)
        elif action == "deactivate":
            response = auth_client.post(f"/users/{user_id}/deactivate", headers=self.admin_headers)
        elif action == "lock":
            response = auth_client.post(
                f"/users/{user_id}/lock", params={"lock_minutes": scenario["lock_minutes"]}, headers=self.admin_headers
            )
        elif action == "unlock":
            response = auth_client.post(f"/users/{user_id}/unlock", headers=self.admin_headers)

        assert response.status_code == scenario["expected_status"]
