"""
ユーザーサービスのテスト

ユーザーサービスのビジネスロジックをテストします。
"""

from datetime import datetime, timezone

import pytest

from app import schemas
from app.services.user import UserService


@pytest.mark.service
class TestUserService:
    """ユーザーサービスのテスト"""

    def test_create_user_success(self, user_service: UserService, db_session):
        """ユーザー作成の成功テスト"""
        user_data = schemas.UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpassword123",
            full_name="Test User",
            role="user",
        )

        user = user_service.create_user(db_session, user_data)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.role == "user"
        assert user.is_active is True
        assert user.hashed_password is not None
        # パスワードが漏洩していないことを確認（hashed_passwordのみ存在し、平文パスワードは存在しない）
        assert "password" not in str(user)

    def test_create_user_duplicate_email(self, user_service: UserService, db_session):
        """重複メールアドレスでのユーザー作成失敗テスト"""
        user_data = schemas.UserCreate(
            email="duplicate@example.com",
            username="user1",
            password="password123",
            full_name="User One",
        )

        # 最初の作成は成功
        user_service.create_user(db_session, user_data)

        # 2回目の作成は失敗（同じメールアドレス）
        duplicate_user_data = schemas.UserCreate(
            email="duplicate@example.com",
            username="user2",
            password="password123",
            full_name="User Two",
        )

        with pytest.raises(ValueError, match="Email already registered"):
            user_service.create_user(db_session, duplicate_user_data)

    def test_create_user_duplicate_username(self, user_service: UserService, db_session):
        """重複ユーザー名でのユーザー作成失敗テスト"""
        user_data = schemas.UserCreate(
            email="user1@example.com",
            username="duplicateuser",
            password="password123",
            full_name="User One",
        )

        # 最初の作成は成功
        user_service.create_user(db_session, user_data)

        # 2回目の作成は失敗（同じユーザー名）
        duplicate_user_data = schemas.UserCreate(
            email="user2@example.com",
            username="duplicateuser",
            password="password123",
            full_name="User Two",
        )

        with pytest.raises(ValueError, match="Username already taken"):
            user_service.create_user(db_session, duplicate_user_data)

    def test_get_user_success(self, user_service: UserService, db_session):
        """ユーザー取得の成功テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="get@example.com",
            username="getuser",
            password="password123",
            full_name="Get User",
        )
        created_user = user_service.create_user(db_session, user_data)

        # ユーザーを取得
        retrieved_user = user_service.get_user(db_session, created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.email == "get@example.com"
        assert retrieved_user.username == "getuser"
        assert retrieved_user.full_name == "Get User"

    def test_get_user_not_found(self, user_service: UserService, db_session):
        """存在しないユーザーの取得テスト"""
        user = user_service.get_user(db_session, "non-existent-id")
        assert user is None

    def test_get_user_by_email_success(self, user_service: UserService, db_session):
        """メールアドレスでのユーザー取得成功テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="email@example.com",
            username="emailuser",
            password="password123",
            full_name="Email User",
        )
        user_service.create_user(db_session, user_data)

        # メールアドレスで取得
        retrieved_user = user_service.get_user_by_email(db_session, "email@example.com")

        assert retrieved_user is not None
        assert retrieved_user.username == "emailuser"
        assert retrieved_user.full_name == "Email User"

    def test_get_user_by_email_not_found(self, user_service: UserService, db_session):
        """存在しないメールアドレスでのユーザー取得テスト"""
        user = user_service.get_user_by_email(db_session, "nonexistent@example.com")
        assert user is None

    def test_get_user_by_username_success(self, user_service: UserService, db_session):
        """ユーザー名でのユーザー取得成功テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="username@example.com",
            username="usernameuser",
            password="password123",
            full_name="Username User",
        )
        user_service.create_user(db_session, user_data)

        # ユーザー名で取得
        retrieved_user = user_service.get_user_by_username(db_session, "usernameuser")

        assert retrieved_user is not None
        assert retrieved_user.email == "username@example.com"
        assert retrieved_user.full_name == "Username User"

    def test_get_user_by_username_not_found(self, user_service: UserService, db_session):
        """存在しないユーザー名でのユーザー取得テスト"""
        user = user_service.get_user_by_username(db_session, "nonexistentuser")
        assert user is None

    def test_get_users_with_pagination(self, user_service: UserService, db_session):
        """ユーザー一覧取得（ページネーション）のテスト"""
        # 複数のユーザーを作成
        users_data = [
            schemas.UserCreate(
                email="user1@example.com",
                username="user1",
                password="password123",
                full_name="User One",
            ),
            schemas.UserCreate(
                email="user2@example.com",
                username="user2",
                password="password123",
                full_name="User Two",
            ),
            schemas.UserCreate(
                email="user3@example.com",
                username="user3",
                password="password123",
                full_name="User Three",
            ),
        ]

        for user_data in users_data:
            user_service.create_user(db_session, user_data)

        # ページネーションテスト
        users = user_service.get_users(db_session, skip=0, limit=2)
        assert len(users) == 2

        users = user_service.get_users(db_session, skip=2, limit=1)
        assert len(users) == 1

    def test_get_active_users(self, user_service: UserService, db_session):
        """アクティブユーザー一覧取得のテスト"""
        # アクティブユーザーを作成
        active_user_data = schemas.UserCreate(
            email="active@example.com",
            username="activeuser",
            password="password123",
            full_name="Active User",
        )
        user_service.create_user(db_session, active_user_data)

        # 非アクティブユーザーを作成
        inactive_user_data = schemas.UserCreate(
            email="inactive@example.com",
            username="inactiveuser",
            password="password123",
            full_name="Inactive User",
        )
        inactive_user = user_service.create_user(db_session, inactive_user_data)
        user_service.deactivate_user(db_session, inactive_user.id)

        active_users = user_service.get_active_users(db_session, skip=0, limit=10)
        assert len(active_users) == 1
        assert active_users[0].email == "active@example.com"

    def test_get_users_by_role(self, user_service: UserService, db_session):
        """役割別ユーザー取得のテスト"""
        # 一般ユーザーを作成
        user_data = schemas.UserCreate(
            email="user@example.com",
            username="normaluser",
            password="password123",
            full_name="Normal User",
            role="user",
        )
        user_service.create_user(db_session, user_data)

        # 管理者ユーザーを作成
        admin_data = schemas.UserCreate(
            email="admin@example.com",
            username="adminuser",
            password="password123",
            full_name="Admin User",
            role="admin",
        )
        user_service.create_user(db_session, admin_data)

        admin_users = user_service.get_users_by_role(db_session, "admin", skip=0, limit=10)
        assert len(admin_users) == 1
        assert admin_users[0].email == "admin@example.com"

    def test_update_user_success(self, user_service: UserService, db_session):
        """ユーザー更新の成功テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="update@example.com",
            username="updateuser",
            password="password123",
            full_name="Update User",
        )
        created_user = user_service.create_user(db_session, user_data)

        # ユーザーを更新
        update_data = schemas.UserUpdate(
            full_name="Updated User",
            bio="Updated bio",
            avatar_url="https://example.com/avatar.jpg",
        )
        updated_user = user_service.update_user(db_session, created_user.id, update_data)

        assert updated_user is not None
        assert updated_user.full_name == "Updated User"
        assert updated_user.bio == "Updated bio"
        assert updated_user.avatar_url == "https://example.com/avatar.jpg"
        assert updated_user.email == "update@example.com"  # 変更されていない

    def test_update_user_not_found(self, user_service: UserService, db_session):
        """存在しないユーザーの更新テスト"""
        update_data = schemas.UserUpdate(full_name="Updated User")
        updated_user = user_service.update_user(db_session, "non-existent-id", update_data)
        assert updated_user is None

    def test_update_user_duplicate_email(self, user_service: UserService, db_session):
        """重複メールアドレスでのユーザー更新失敗テスト"""
        # 2つのユーザーを作成
        user1_data = schemas.UserCreate(
            email="user1@example.com",
            username="user1",
            password="password123",
            full_name="User One",
        )
        user1 = user_service.create_user(db_session, user1_data)

        user2_data = schemas.UserCreate(
            email="user2@example.com",
            username="user2",
            password="password123",
            full_name="User Two",
        )
        user_service.create_user(db_session, user2_data)

        # user1のメールアドレスをuser2と同じに変更しようとする
        update_data = schemas.UserUpdate(email="user2@example.com")

        with pytest.raises(ValueError, match="Email already registered"):
            user_service.update_user(db_session, user1.id, update_data)

    def test_update_user_duplicate_username(self, user_service: UserService, db_session):
        """重複ユーザー名でのユーザー更新失敗テスト"""
        # 2つのユーザーを作成
        user1_data = schemas.UserCreate(
            email="user1@example.com",
            username="user1",
            password="password123",
            full_name="User One",
        )
        user1 = user_service.create_user(db_session, user1_data)

        user2_data = schemas.UserCreate(
            email="user2@example.com",
            username="user2",
            password="password123",
            full_name="User Two",
        )
        user_service.create_user(db_session, user2_data)

        # user1のユーザー名をuser2と同じに変更しようとする
        update_data = schemas.UserUpdate(username="user2")

        with pytest.raises(ValueError, match="Username already taken"):
            user_service.update_user(db_session, user1.id, update_data)

    def test_update_password_success(self, user_service: UserService, db_session):
        """パスワード更新の成功テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="password@example.com",
            username="passworduser",
            password="oldpassword123",
            full_name="Password User",
        )
        created_user = user_service.create_user(db_session, user_data)

        # パスワードを更新
        new_password = "newpassword123"
        updated_user = user_service.update_password(db_session, created_user.id, new_password)

        assert updated_user is not None
        assert updated_user.hashed_password is not None
        assert updated_user.hashed_password != "newpassword123"  # ハッシュ化されていることを確認

    def test_update_password_not_found(self, user_service: UserService, db_session):
        """存在しないユーザーのパスワード更新テスト"""
        updated_user = user_service.update_password(db_session, "non-existent-id", "newpassword123")
        assert updated_user is None

    def test_update_last_login_success(self, user_service: UserService, db_session):
        """最終ログイン日時更新の成功テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="login@example.com",
            username="loginuser",
            password="password123",
            full_name="Login User",
        )
        created_user = user_service.create_user(db_session, user_data)

        # 最終ログイン日時を更新
        updated_user = user_service.update_last_login(db_session, created_user.id)

        assert updated_user is not None
        assert updated_user.last_login is not None
        # ISO形式の日時文字列であることを確認
        datetime.fromisoformat(updated_user.last_login)

    def test_update_last_login_not_found(self, user_service: UserService, db_session):
        """存在しないユーザーの最終ログイン日時更新テスト"""
        updated_user = user_service.update_last_login(db_session, "non-existent-id")
        assert updated_user is None

    def test_increment_failed_attempts_success(self, user_service: UserService, db_session):
        """ログイン失敗回数増加の成功テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="failed@example.com",
            username="faileduser",
            password="password123",
            full_name="Failed User",
        )
        created_user = user_service.create_user(db_session, user_data)

        # 初期状態は0
        assert created_user.failed_login_attempts == "0"

        # 失敗回数を増加
        updated_user = user_service.increment_failed_attempts(db_session, created_user.id)
        assert updated_user is not None
        assert updated_user.failed_login_attempts == "1"

        # さらに増加
        updated_user = user_service.increment_failed_attempts(db_session, created_user.id)
        assert updated_user is not None
        assert updated_user.failed_login_attempts == "2"

    def test_increment_failed_attempts_not_found(self, user_service: UserService, db_session):
        """存在しないユーザーの失敗回数増加テスト"""
        updated_user = user_service.increment_failed_attempts(db_session, "non-existent-id")
        assert updated_user is None

    def test_reset_failed_attempts_success(self, user_service: UserService, db_session):
        """ログイン失敗回数リセットの成功テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="reset@example.com",
            username="resetuser",
            password="password123",
            full_name="Reset User",
        )
        created_user = user_service.create_user(db_session, user_data)

        # 失敗回数を増加
        user_service.increment_failed_attempts(db_session, created_user.id)
        user_service.increment_failed_attempts(db_session, created_user.id)

        # リセット
        updated_user = user_service.reset_failed_attempts(db_session, created_user.id)
        assert updated_user is not None
        assert updated_user.failed_login_attempts == "0"
        assert updated_user.locked_until is None

    def test_reset_failed_attempts_not_found(self, user_service: UserService, db_session):
        """存在しないユーザーの失敗回数リセットテスト"""
        updated_user = user_service.reset_failed_attempts(db_session, "non-existent-id")
        assert updated_user is None

    def test_lock_account_success(self, user_service: UserService, db_session):
        """アカウントロックの成功テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="lock@example.com",
            username="lockuser",
            password="password123",
            full_name="Lock User",
        )
        created_user = user_service.create_user(db_session, user_data)

        # アカウントをロック
        updated_user = user_service.lock_account(db_session, created_user.id, lock_minutes=30)

        assert updated_user is not None
        assert updated_user.locked_until is not None
        # ロック期限が未来であることを確認
        lock_time = datetime.fromisoformat(updated_user.locked_until)
        assert lock_time > datetime.now(timezone.utc)

    def test_lock_account_not_found(self, user_service: UserService, db_session):
        """存在しないユーザーのアカウントロックテスト"""
        updated_user = user_service.lock_account(db_session, "non-existent-id", lock_minutes=30)
        assert updated_user is None

    def test_unlock_account_success(self, user_service: UserService, db_session):
        """アカウントロック解除の成功テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="unlock@example.com",
            username="unlockuser",
            password="password123",
            full_name="Unlock User",
        )
        created_user = user_service.create_user(db_session, user_data)

        # アカウントをロック
        user_service.lock_account(db_session, created_user.id, lock_minutes=30)

        # ロックを解除
        updated_user = user_service.unlock_account(db_session, created_user.id)
        assert updated_user is not None
        assert updated_user.locked_until is None

    def test_unlock_account_not_found(self, user_service: UserService, db_session):
        """存在しないユーザーのアカウントロック解除テスト"""
        updated_user = user_service.unlock_account(db_session, "non-existent-id")
        assert updated_user is None

    def test_deactivate_user_success(self, user_service: UserService, db_session):
        """ユーザー無効化の成功テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="deactivate@example.com",
            username="deactivateuser",
            password="password123",
            full_name="Deactivate User",
        )
        created_user = user_service.create_user(db_session, user_data)

        # 初期状態はアクティブ
        assert created_user.is_active is True

        # 無効化
        updated_user = user_service.deactivate_user(db_session, created_user.id)
        assert updated_user is not None
        assert updated_user.is_active is False

    def test_deactivate_user_not_found(self, user_service: UserService, db_session):
        """存在しないユーザーの無効化テスト"""
        updated_user = user_service.deactivate_user(db_session, "non-existent-id")
        assert updated_user is None

    def test_activate_user_success(self, user_service: UserService, db_session):
        """ユーザー有効化の成功テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="activate@example.com",
            username="activateuser",
            password="password123",
            full_name="Activate User",
        )
        created_user = user_service.create_user(db_session, user_data)

        # 無効化
        user_service.deactivate_user(db_session, created_user.id)

        # 有効化
        updated_user = user_service.activate_user(db_session, created_user.id)
        assert updated_user is not None
        assert updated_user.is_active is True

    def test_activate_user_not_found(self, user_service: UserService, db_session):
        """存在しないユーザーの有効化テスト"""
        updated_user = user_service.activate_user(db_session, "non-existent-id")
        assert updated_user is None

    def test_delete_user_success(self, user_service: UserService, db_session):
        """ユーザー削除の成功テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="delete@example.com",
            username="deleteuser",
            password="password123",
            full_name="Delete User",
        )
        created_user = user_service.create_user(db_session, user_data)

        # 削除
        success = user_service.delete_user(db_session, created_user.id)
        assert success is True

        # 削除されたことを確認
        deleted_user = user_service.get_user(db_session, created_user.id)
        assert deleted_user is None

    def test_delete_user_not_found(self, user_service: UserService, db_session):
        """存在しないユーザーの削除テスト"""
        success = user_service.delete_user(db_session, "non-existent-id")
        assert success is False

    def test_exists_user_by_email(self, user_service: UserService, db_session):
        """メールアドレスでのユーザー存在確認テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="exists@example.com",
            username="existsuser",
            password="password123",
            full_name="Exists User",
        )
        user_service.create_user(db_session, user_data)

        # 存在確認
        assert user_service.exists_user(db_session, email="exists@example.com") is True
        assert user_service.exists_user(db_session, email="nonexistent@example.com") is False

    def test_exists_user_by_username(self, user_service: UserService, db_session):
        """ユーザー名でのユーザー存在確認テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="exists@example.com",
            username="existsuser",
            password="password123",
            full_name="Exists User",
        )
        user_service.create_user(db_session, user_data)

        # 存在確認
        assert user_service.exists_user(db_session, username="existsuser") is True
        assert user_service.exists_user(db_session, username="nonexistentuser") is False

    def test_count_users(self, user_service: UserService, db_session):
        """ユーザー数取得のテスト"""
        # 初期状態
        assert user_service.count_users(db_session) == 0

        # ユーザーを作成
        users_data = [
            schemas.UserCreate(
                email="user1@example.com",
                username="user1",
                password="password123",
                full_name="User One",
            ),
            schemas.UserCreate(
                email="user2@example.com",
                username="user2",
                password="password123",
                full_name="User Two",
            ),
            schemas.UserCreate(
                email="user3@example.com",
                username="user3",
                password="password123",
                full_name="User Three",
            ),
        ]

        for user_data in users_data:
            user_service.create_user(db_session, user_data)

        assert user_service.count_users(db_session) == 3

    def test_count_active_users(self, user_service: UserService, db_session):
        """アクティブユーザー数取得のテスト"""
        # アクティブユーザーを作成
        active_user_data = schemas.UserCreate(
            email="active_count@example.com",
            username="activecountuser",
            password="password123",
            full_name="Active Count User",
        )
        user_service.create_user(db_session, active_user_data)

        # 非アクティブユーザーを作成
        inactive_user_data = schemas.UserCreate(
            email="inactive_count@example.com",
            username="inactivecountuser",
            password="password123",
            full_name="Inactive Count User",
        )
        inactive_user = user_service.create_user(db_session, inactive_user_data)
        user_service.deactivate_user(db_session, inactive_user.id)

        assert user_service.count_active_users(db_session) == 1

    def test_count_users_by_role(self, user_service: UserService, db_session):
        """役割別ユーザー数取得のテスト"""
        # 一般ユーザーを作成
        user_data = schemas.UserCreate(
            email="role_count@example.com",
            username="rolecountuser",
            password="password123",
            full_name="Role Count User",
            role="user",
        )
        user_service.create_user(db_session, user_data)

        # 管理者ユーザーを作成
        admin_data = schemas.UserCreate(
            email="admin_count@example.com",
            username="admincountuser",
            password="password123",
            full_name="Admin Count User",
            role="admin",
        )
        user_service.create_user(db_session, admin_data)

        assert user_service.count_users_by_role(db_session, "user") == 1
        assert user_service.count_users_by_role(db_session, "admin") == 1
        assert user_service.count_users_by_role(db_session, "moderator") == 0

    def test_create_user_with_custom_role(self, user_service: UserService, db_session):
        """カスタム役割でのユーザー作成テスト"""
        user_data = schemas.UserCreate(
            email="moderator@example.com",
            username="moderatoruser",
            password="password123",
            full_name="Moderator User",
            role="moderator",
        )

        user = user_service.create_user(db_session, user_data)

        assert user.role == "moderator"
        assert user.is_active is True

    def test_create_user_with_optional_fields(self, user_service: UserService, db_session):
        """オプションフィールド付きでのユーザー作成テスト"""
        user_data = schemas.UserCreate(
            email="optional@example.com",
            username="optionaluser",
            password="password123",
            full_name="Optional User",
            avatar_url="https://example.com/avatar.jpg",
            bio="This is a test user",
        )

        user = user_service.create_user(db_session, user_data)

        assert user.avatar_url == "https://example.com/avatar.jpg"
        assert user.bio == "This is a test user"

    def test_update_user_partial_fields(self, user_service: UserService, db_session):
        """部分フィールドでのユーザー更新テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="partial@example.com",
            username="partialuser",
            password="password123",
            full_name="Partial User",
            bio="Original bio",
        )
        created_user = user_service.create_user(db_session, user_data)

        # 部分更新（bioのみ）
        update_data = schemas.UserUpdate(bio="Updated bio")
        updated_user = user_service.update_user(db_session, created_user.id, update_data)

        assert updated_user is not None
        assert updated_user.bio == "Updated bio"
        assert updated_user.full_name == "Partial User"  # 変更されていない
        assert updated_user.email == "partial@example.com"  # 変更されていない

    def test_update_user_with_none_values(self, user_service: UserService, db_session):
        """None値を含むユーザー更新テスト"""
        # ユーザーを作成
        user_data = schemas.UserCreate(
            email="none@example.com",
            username="noneuser",
            password="password123",
            full_name="None User",
            bio="Original bio",
        )
        created_user = user_service.create_user(db_session, user_data)

        # None値を含む更新データ
        update_data = schemas.UserUpdate(bio=None, avatar_url=None)
        updated_user = user_service.update_user(db_session, created_user.id, update_data)

        assert updated_user is not None
        # Pydantic v2では明示的にNoneを渡すとNoneで上書きされるのが正しい挙動
        assert updated_user.bio is None  # Noneで上書きされる
        assert updated_user.avatar_url is None  # 元々Noneなので変更されない
