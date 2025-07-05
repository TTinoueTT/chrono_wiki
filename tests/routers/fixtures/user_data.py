"""
ユーザーテスト用のデータフィクスチャ

テストシナリオ用のユーザーデータを提供します。
"""

from typing import Any, Dict, List

from app.enums import UserRole


class UserTestScenarios:
    """ユーザーテスト用のシナリオデータ"""

    @staticmethod
    def registration_scenarios() -> List[Dict[str, Any]]:
        """ユーザー登録テストシナリオ"""
        return [
            {
                "name": "valid_user",
                "data": {
                    "email": "valid@example.com",
                    "username": "validuser",
                    "password": "validpassword123",
                    "full_name": "Valid User",
                    "role": "user",
                },
                "expected_status": 201,
                "description": "有効なユーザーデータでの登録",
            },
            {
                "name": "duplicate_email",
                "data": {
                    "email": "duplicate@example.com",
                    "username": "differentuser",
                    "password": "password123",
                    "full_name": "Duplicate User",
                    "role": "user",
                },
                "expected_status": 400,
                "description": "重複メールアドレスでの登録失敗",
            },
            {
                "name": "duplicate_username",
                "data": {
                    "email": "different@example.com",
                    "username": "duplicateuser",
                    "password": "password123",
                    "full_name": "Duplicate Username User",
                    "role": "user",
                },
                "expected_status": 400,
                "description": "重複ユーザー名での登録失敗",
            },
            {
                "name": "missing_username",
                "data": {
                    "email": "missing@example.com",
                    "password": "password123",
                    "full_name": "Missing Username User",
                    "role": "user",
                },
                "expected_status": 422,
                "description": "ユーザー名不足での登録失敗",
            },
            {
                "name": "invalid_email",
                "data": {
                    "email": "invalid-email",
                    "username": "invaliduser",
                    "password": "password123",
                    "full_name": "Invalid Email User",
                    "role": "user",
                },
                "expected_status": 422,
                "description": "無効なメールアドレスでの登録失敗",
            },
            {
                "name": "short_password",
                "data": {
                    "email": "short@example.com",
                    "username": "shortuser",
                    "password": "123",
                    "full_name": "Short Password User",
                    "role": "user",
                },
                "expected_status": 422,
                "description": "短いパスワードでの登録失敗",
            },
        ]

    @staticmethod
    def login_scenarios() -> List[Dict[str, Any]]:
        """ログインテストシナリオ"""
        return [
            {
                "name": "valid_credentials_email",
                "login_data": {"username": "test@example.com", "password": "testpassword123"},
                "expected_status": 200,
                "description": "有効なメールアドレス・パスワードでのログイン",
            },
            {
                "name": "valid_credentials_username",
                "login_data": {"username": "testuser", "password": "testpassword123"},
                "expected_status": 200,
                "description": "有効なユーザー名・パスワードでのログイン",
            },
            {
                "name": "invalid_password",
                "login_data": {"username": "test@example.com", "password": "wrongpassword"},
                "expected_status": 401,
                "description": "間違ったパスワードでのログイン失敗",
            },
            {
                "name": "nonexistent_user",
                "login_data": {"username": "nonexistent@example.com", "password": "testpassword123"},
                "expected_status": 401,
                "description": "存在しないユーザーでのログイン失敗",
            },
        ]

    @staticmethod
    def password_change_scenarios() -> List[Dict[str, Any]]:
        """パスワード変更テストシナリオ"""
        return [
            {
                "name": "valid_password_change",
                "current_password": "testpassword123",
                "new_password": "newpassword123",
                "expected_status": 200,
                "description": "有効なパスワード変更",
            },
            {
                "name": "wrong_current_password",
                "current_password": "wrongpassword",
                "new_password": "newpassword123",
                "expected_status": 400,
                "description": "間違った現在のパスワードでの変更失敗",
            },
            {
                "name": "short_new_password",
                "current_password": "testpassword123",
                "new_password": "123",
                "expected_status": 422,
                "description": "短い新しいパスワードでの変更失敗",
            },
        ]

    @staticmethod
    def user_management_scenarios() -> List[Dict[str, Any]]:
        """ユーザー管理テストシナリオ"""
        return [
            {"name": "activate_user", "action": "activate", "expected_status": 200, "description": "ユーザー有効化"},
            {
                "name": "deactivate_user",
                "action": "deactivate",
                "expected_status": 200,
                "description": "ユーザー無効化",
            },
            {
                "name": "lock_user",
                "action": "lock",
                "lock_minutes": 30,
                "expected_status": 200,
                "description": "ユーザーアカウントロック",
            },
            {
                "name": "unlock_user",
                "action": "unlock",
                "expected_status": 200,
                "description": "ユーザーアカウントロック解除",
            },
        ]


class UserTestData:
    """ユーザーテストデータ生成クラス"""

    @staticmethod
    def create_user_data(
        email: str = "test@example.com",
        username: str = "testuser",
        password: str = "testpassword123",
        full_name: str = "Test User",
        role: str = UserRole.USER.value,
        is_active: bool = True,
    ) -> Dict[str, Any]:
        """基本的なユーザーデータを生成"""
        return {
            "email": email,
            "username": username,
            "password": password,
            "full_name": full_name,
            "role": role,
            "is_active": is_active,
        }

    @staticmethod
    def create_admin_data() -> Dict[str, Any]:
        """管理者ユーザーデータを生成"""
        return UserTestData.create_user_data(
            email="admin@example.com",
            username="adminuser",
            password="adminpassword123",
            full_name="Admin User",
            role=UserRole.ADMIN.value,
        )

    @staticmethod
    def create_moderator_data() -> Dict[str, Any]:
        """モデレーターユーザーデータを生成"""
        return UserTestData.create_user_data(
            email="moderator@example.com",
            username="moderatoruser",
            password="moderatorpassword123",
            full_name="Moderator User",
            role=UserRole.MODERATOR.value,
        )

    @staticmethod
    def create_sample_users() -> List[Dict[str, Any]]:
        """サンプルユーザーリストを生成"""
        return [
            UserTestData.create_user_data(email="user1@example.com", username="user1", full_name="User One"),
            UserTestData.create_user_data(email="user2@example.com", username="user2", full_name="User Two"),
            UserTestData.create_user_data(email="user3@example.com", username="user3", full_name="User Three"),
        ]
