"""
ユーザールーターの結合テスト

ユーザーエンドポイントの統合テストを実装します。
実際のデータベースとサービスを使用してテストします。
"""

import pytest
from fastapi import status

from tests.routers.fixtures.user_data import UserTestData, UserTestScenarios


@pytest.mark.router
@pytest.mark.integration
class TestUserManagement:
    """ユーザー管理系テスト（管理者権限）"""

    def test_user_management_as_admin(self, auth_client, sample_user_data, admin_user_data):
        """管理者としてのユーザー管理テスト"""
        # 一般ユーザーを作成
        register_response = auth_client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        user_id = register_response.json()["id"]

        # 管理者ユーザーを作成
        admin_register_response = auth_client.post("/api/v1/auth/register", json=admin_user_data)
        assert admin_register_response.status_code == status.HTTP_201_CREATED

        # 管理者でログイン
        login_data = {
            "username": admin_user_data["email"],
            "password": admin_user_data["password"],
        }
        login_response = auth_client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # ユーザーを無効化
        deactivate_response = auth_client.post(f"/api/v1/users/{user_id}/deactivate", headers=headers)
        assert deactivate_response.status_code == status.HTTP_200_OK
        assert deactivate_response.json()["is_active"] is False

        # ユーザーを有効化
        activate_response = auth_client.post(f"/api/v1/users/{user_id}/activate", headers=headers)
        assert activate_response.status_code == status.HTTP_200_OK
        assert activate_response.json()["is_active"] is True


@pytest.mark.router
@pytest.mark.integration
class TestUserAnalytics:
    """ユーザー分析・統計系テスト（モデレーター権限）"""

    def test_user_stats_as_moderator(self, auth_client, moderator_user_data):
        """モデレーターとしてのユーザー統計取得テスト"""
        # モデレーターユーザーを作成
        register_response = auth_client.post("/api/v1/auth/register", json=moderator_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        login_data = {
            "username": moderator_user_data["email"],
            "password": moderator_user_data["password"],
        }
        login_response = auth_client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 統計を取得
        response = auth_client.get("/api/v1/users/stats/count", headers=headers)

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
        register_response = auth_client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        user_id = register_response.json()["id"]

        # 2. ログイン
        login_data = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"],
        }
        login_response = auth_client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. ユーザー情報更新
        update_data = {
            "full_name": "Updated User",
            "bio": "Updated bio",
        }
        update_response = auth_client.put(f"/api/v1/users/{user_id}", json=update_data, headers=headers)
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["full_name"] == "Updated User"

        # 4. パスワード変更
        change_password_response = auth_client.post(
            "/api/v1/auth/change-password",
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
        new_login_response = auth_client.post("/api/v1/auth/login", data=new_login_data)
        assert new_login_response.status_code == status.HTTP_200_OK

        # 6. ログアウト
        logout_response = auth_client.post("/api/v1/auth/logout", headers=headers)
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
        auth_client.post("/api/v1/auth/register", json=user_data)

        # ログイン
        login_response = auth_client.post(
            "/api/v1/auth/login", data={"username": f"{role}@example.com", "password": f"{role}password123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 管理者エンドポイントにアクセス
        response = auth_client.get("/api/v1/users/", headers=headers)

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
        auth_client.post("/api/v1/auth/register", json=user_data)

        # ログイン
        login_response = auth_client.post(
            "/api/v1/auth/login", data={"username": f"{role}@example.com", "password": f"{role}password123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # モデレーターエンドポイントにアクセス
        response = auth_client.get("/api/v1/users/stats/count", headers=headers)

        if can_access_moderator_endpoints:
            assert response.status_code == status.HTTP_200_OK
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN


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
        admin_register = auth_client.post("/api/v1/auth/register", json=admin_data)
        self.admin_user = admin_register.json()

        # 管理者でログイン
        admin_login = auth_client.post(
            "/api/v1/auth/login", data={"username": "admin@example.com", "password": "adminpassword123"}
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
        user_register = auth_client.post("/api/v1/auth/register", json=user_data)
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
            response = auth_client.post(f"/api/v1/users/{user_id}/activate", headers=self.admin_headers)
        elif action == "deactivate":
            response = auth_client.post(f"/api/v1/users/{user_id}/deactivate", headers=self.admin_headers)
        elif action == "lock":
            response = auth_client.post(
                f"/api/v1/users/{user_id}/lock",
                params={"lock_minutes": scenario["lock_minutes"]},
                headers=self.admin_headers,
            )
        elif action == "unlock":
            response = auth_client.post(f"/api/v1/users/{user_id}/unlock", headers=self.admin_headers)

        assert response.status_code == scenario["expected_status"]


@pytest.mark.router
@pytest.mark.integration
class TestUserPermissionScenarios:
    """ユーザー権限・認証シナリオのテスト"""

    @pytest.fixture(autouse=True)
    def setup_test_users(self, auth_client):
        """テスト用ユーザーをセットアップ"""
        # 管理者ユーザーを作成
        admin_data = UserTestData.create_admin_data()
        admin_register = auth_client.post("/api/v1/auth/register", json=admin_data)
        self.admin_user = admin_register.json()

        # 管理者でログイン
        admin_login = auth_client.post(
            "/api/v1/auth/login", data={"username": admin_data["email"], "password": admin_data["password"]}
        )
        self.admin_token = admin_login.json()["access_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

        # 一般ユーザーを作成
        user_data = UserTestData.create_user_data(
            email="permission@example.com", username="permissionuser", full_name="Permission User"
        )
        user_register = auth_client.post("/api/v1/auth/register", json=user_data)
        self.normal_user = user_register.json()

        # 一般ユーザーでログイン
        user_login = auth_client.post(
            "/api/v1/auth/login", data={"username": user_data["email"], "password": user_data["password"]}
        )
        self.user_token = user_login.json()["access_token"]
        self.user_headers = {"Authorization": f"Bearer {self.user_token}"}

    @pytest.mark.parametrize(
        "endpoint,method,expected_status",
        [
            ("/api/v1/users/", "GET", status.HTTP_403_FORBIDDEN),  # 管理者専用
            ("/api/v1/users/active", "GET", status.HTTP_403_FORBIDDEN),  # モデレーター以上
            ("/api/v1/users/role/user", "GET", status.HTTP_403_FORBIDDEN),  # モデレーター以上
            ("/api/v1/users/stats/count", "GET", status.HTTP_403_FORBIDDEN),  # モデレーター以上
            ("/api/v1/users/stats/role/user/count", "GET", status.HTTP_403_FORBIDDEN),  # モデレーター以上
        ],
    )
    def test_moderator_endpoints_access_denied(self, auth_client, endpoint, method, expected_status):
        """モデレーター権限が必要なエンドポイントへのアクセス拒否テスト"""
        response = auth_client.request(method, endpoint, headers=self.user_headers)
        assert response.status_code == expected_status

    def test_get_user_permission_denied(self, auth_client):
        """権限不足でのユーザー詳細取得テスト（403 Forbidden）"""
        other_user_id = self.admin_user["id"]
        response = auth_client.get(f"/api/v1/users/{other_user_id}", headers=self.user_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]

    def test_update_user_permission_denied(self, auth_client):
        """権限不足でのユーザー更新テスト（403 Forbidden）"""
        other_user_id = self.admin_user["id"]
        update_data = {"full_name": "Updated Name"}
        response = auth_client.put(f"/api/v1/users/{other_user_id}", json=update_data, headers=self.user_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]

    def test_self_access_allowed(self, auth_client):
        """自分自身へのアクセスが許可されるテスト"""
        user_id = self.normal_user["id"]
        response = auth_client.get(f"/api/v1/users/{user_id}", headers=self.user_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == user_id

    def test_self_update_allowed(self, auth_client):
        """自分自身の更新が許可されるテスト"""
        user_id = self.normal_user["id"]
        update_data = {"full_name": "Updated Self Name"}
        response = auth_client.put(f"/api/v1/users/{user_id}", json=update_data, headers=self.user_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["full_name"] == "Updated Self Name"

    def test_admin_access_other_user(self, auth_client):
        """管理者が他のユーザーにアクセスできるテスト"""
        user_id = self.normal_user["id"]
        response = auth_client.get(f"/api/v1/users/{user_id}", headers=self.admin_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == user_id

    def test_admin_update_other_user(self, auth_client):
        """管理者が他のユーザーを更新できるテスト"""
        user_id = self.normal_user["id"]
        update_data = {"full_name": "Admin Updated Name"}
        response = auth_client.put(f"/api/v1/users/{user_id}", json=update_data, headers=self.admin_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["full_name"] == "Admin Updated Name"


@pytest.mark.router
@pytest.mark.integration
class TestUserErrorScenarios:
    """ユーザーエラー・異常系シナリオのテスト"""

    @pytest.fixture(autouse=True)
    def setup_admin_user(self, auth_client):
        """管理者ユーザーをセットアップ"""
        admin_data = UserTestData.create_admin_data()
        admin_register = auth_client.post("/api/v1/auth/register", json=admin_data)
        self.admin_user = admin_register.json()

        admin_login = auth_client.post(
            "/api/v1/auth/login", data={"username": admin_data["email"], "password": admin_data["password"]}
        )
        self.admin_token = admin_login.json()["access_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

    @pytest.mark.parametrize(
        "endpoint,method,user_id,expected_status",
        [
            ("/api/v1/users/{user_id}", "GET", "non-existent-user-id", status.HTTP_404_NOT_FOUND),
            ("/api/v1/users/{user_id}", "PUT", "non-existent-user-id", status.HTTP_404_NOT_FOUND),
            ("/api/v1/users/{user_id}", "DELETE", "non-existent-user-id", status.HTTP_404_NOT_FOUND),
            ("/api/v1/users/{user_id}/activate", "POST", "non-existent-user-id", status.HTTP_404_NOT_FOUND),
            ("/api/v1/users/{user_id}/deactivate", "POST", "non-existent-user-id", status.HTTP_404_NOT_FOUND),
            ("/api/v1/users/{user_id}/lock", "POST", "non-existent-user-id", status.HTTP_404_NOT_FOUND),
            ("/api/v1/users/{user_id}/unlock", "POST", "non-existent-user-id", status.HTTP_404_NOT_FOUND),
        ],
    )
    def test_user_not_found_scenarios(self, auth_client, endpoint, method, user_id, expected_status):
        """存在しないユーザーに対する操作のテスト"""
        url = endpoint.format(user_id=user_id)
        if method == "PUT":
            response = auth_client.put(url, json={"full_name": "Test"}, headers=self.admin_headers)
        else:
            response = auth_client.request(method, url, headers=self.admin_headers)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_404_NOT_FOUND:
            assert "User not found" in response.json()["detail"]

    def test_update_user_value_error(self, auth_client):
        """ユーザー更新時のValueErrorテスト（400 Bad Request）"""
        # 新しいユーザーを作成
        user_data = UserTestData.create_user_data(
            email="valueerror@example.com", username="valueerroruser", full_name="ValueError User"
        )
        user_register = auth_client.post("/api/v1/auth/register", json=user_data)
        user_id = user_register.json()["id"]

        # 無効なデータでユーザーを更新しようとする
        update_data = {"email": "invalid-email"}  # 無効なメールアドレス
        response = auth_client.put(f"/api/v1/users/{user_id}", json=update_data, headers=self.admin_headers)
        # 実際のバリデーション結果に応じてステータスコードが変わる可能性がある
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


@pytest.mark.router
@pytest.mark.integration
class TestUserManagementWorkflow:
    """ユーザー管理ワークフローの統合テスト"""

    @pytest.fixture(autouse=True)
    def setup_admin_user(self, auth_client):
        """管理者ユーザーをセットアップ"""
        admin_data = UserTestData.create_admin_data()
        admin_register = auth_client.post("/api/v1/auth/register", json=admin_data)
        self.admin_user = admin_register.json()

        admin_login = auth_client.post(
            "/api/v1/auth/login", data={"username": admin_data["email"], "password": admin_data["password"]}
        )
        self.admin_token = admin_login.json()["access_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

    @pytest.mark.parametrize(
        "scenario",
        UserTestScenarios.user_management_scenarios(),
        ids=[s["name"] for s in UserTestScenarios.user_management_scenarios()],
    )
    def test_user_management_scenarios(self, auth_client, scenario):
        """ユーザー管理の様々なシナリオをテスト"""
        # 新しいユーザーを作成
        user_data = UserTestData.create_user_data(
            email=f"{scenario['name']}@example.com",
            username=f"{scenario['name']}user",
            full_name=f"{scenario['name'].title()} User",
        )
        user_register = auth_client.post("/api/v1/auth/register", json=user_data)
        user_id = user_register.json()["id"]

        action = scenario["action"]
        if action == "activate":
            response = auth_client.post(f"/api/v1/users/{user_id}/activate", headers=self.admin_headers)
        elif action == "deactivate":
            response = auth_client.post(f"/api/v1/users/{user_id}/deactivate", headers=self.admin_headers)
        elif action == "lock":
            lock_minutes = scenario.get("lock_minutes", 30)
            response = auth_client.post(
                f"/api/v1/users/{user_id}/lock", params={"lock_minutes": lock_minutes}, headers=self.admin_headers
            )
        elif action == "unlock":
            response = auth_client.post(f"/api/v1/users/{user_id}/unlock", headers=self.admin_headers)

        assert response.status_code == scenario["expected_status"]

    def test_complete_user_management_workflow(self, auth_client):
        """ユーザー管理の完全なワークフローテスト"""
        # 新しいユーザーを作成
        user_data = UserTestData.create_user_data(
            email="workflow@example.com", username="workflowuser", full_name="Workflow User"
        )
        register_response = auth_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        new_user_id = register_response.json()["id"]

        # 1. ユーザーを無効化
        deactivate_response = auth_client.post(f"/api/v1/users/{new_user_id}/deactivate", headers=self.admin_headers)
        assert deactivate_response.status_code == status.HTTP_200_OK
        assert deactivate_response.json()["is_active"] is False

        # 2. ユーザーを有効化
        activate_response = auth_client.post(f"/api/v1/users/{new_user_id}/activate", headers=self.admin_headers)
        assert activate_response.status_code == status.HTTP_200_OK
        assert activate_response.json()["is_active"] is True

        # 3. ユーザーをロック
        lock_response = auth_client.post(f"/api/v1/users/{new_user_id}/lock", headers=self.admin_headers)
        assert lock_response.status_code == status.HTTP_200_OK
        assert lock_response.json()["locked_until"] is not None

        # 4. ユーザーのロックを解除
        unlock_response = auth_client.post(f"/api/v1/users/{new_user_id}/unlock", headers=self.admin_headers)
        assert unlock_response.status_code == status.HTTP_200_OK
        assert unlock_response.json()["locked_until"] is None

        # 5. ユーザーを削除
        delete_response = auth_client.delete(f"/api/v1/users/{new_user_id}", headers=self.admin_headers)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.router
@pytest.mark.integration
class TestUserPaginationAndStatistics:
    """ユーザーページネーション・統計機能のテスト"""

    @pytest.fixture(autouse=True)
    def setup_admin_user(self, auth_client):
        """管理者ユーザーをセットアップ"""
        admin_data = UserTestData.create_admin_data()
        admin_register = auth_client.post("/api/v1/auth/register", json=admin_data)
        self.admin_user = admin_register.json()

        admin_login = auth_client.post(
            "/api/v1/auth/login", data={"username": admin_data["email"], "password": admin_data["password"]}
        )
        self.admin_token = admin_login.json()["access_token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

    def test_pagination_parameters(self, auth_client):
        """ページネーションパラメータのテスト"""
        # 管理者エンドポイントでページネーションをテスト
        response = auth_client.get("/api/v1/users/?skip=0&limit=5", headers=self.admin_headers)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

        # アクティブユーザーエンドポイントでページネーションをテスト
        response = auth_client.get("/api/v1/users/active?skip=0&limit=5", headers=self.admin_headers)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

        # 役割別ユーザーエンドポイントでページネーションをテスト
        response = auth_client.get("/api/v1/users/role/user?skip=0&limit=5", headers=self.admin_headers)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_statistics_endpoints(self, auth_client):
        """統計エンドポイントのテスト"""
        # ユーザー統計を取得
        response = auth_client.get("/api/v1/users/stats/count", headers=self.admin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_users" in data
        assert "active_users" in data
        assert "inactive_users" in data
        assert isinstance(data["total_users"], int)
        assert isinstance(data["active_users"], int)
        assert isinstance(data["inactive_users"], int)

        # 役割別ユーザー数を取得
        response = auth_client.get("/api/v1/users/stats/role/user/count", headers=self.admin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "role" in data
        assert "count" in data
        assert data["role"] == "user"
        assert isinstance(data["count"], int)

    def test_multiple_users_statistics(self, auth_client):
        """複数ユーザー作成後の統計テスト"""
        # 複数のユーザーを作成
        sample_users = UserTestData.create_sample_users()
        for user_data in sample_users:
            auth_client.post("/api/v1/auth/register", json=user_data)

        # 統計を取得して確認
        response = auth_client.get("/api/v1/users/stats/count", headers=self.admin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 作成したユーザー数分増加していることを確認
        assert data["total_users"] >= len(sample_users)
        assert data["active_users"] >= len(sample_users)
