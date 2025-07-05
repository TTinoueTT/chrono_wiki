"""
CRUD tests for User entity.

UserCRUDクラスのテストケースを実装します。
"""

from datetime import datetime, timezone

import pytest

from app.crud.user import UserCRUD
from app.schemas import UserUpdate

from .conftest import UserTestData


@pytest.mark.crud
class TestUserCRUD:
    """ユーザーCRUD操作のテスト"""

    @pytest.fixture
    def user_crud(self):
        """UserCRUDインスタンス"""
        return UserCRUD()

    def test_create_user(self, user_crud, db_session):
        """ユーザー作成のテスト"""
        user_data = UserTestData.create_user_data()

        user = user_crud.create(db_session, obj_in=user_data)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.role == "user"
        assert user.hashed_password is not None

    def test_get_user(self, user_crud, db_session):
        """ユーザー取得のテスト"""
        user_data = UserTestData.create_user_data(email="get@example.com", username="getuser", full_name="Get User")
        created_user = user_crud.create(db_session, obj_in=user_data)

        retrieved_user = user_crud.get(db_session, created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.email == "get@example.com"
        assert retrieved_user.username == "getuser"
        assert retrieved_user.full_name == "Get User"

    def test_get_user_by_email(self, user_crud, db_session):
        """メールアドレスでのユーザー取得テスト"""
        user_data = UserTestData.create_user_data(
            email="email@example.com", username="emailuser", full_name="Email User"
        )
        user_crud.create(db_session, obj_in=user_data)

        user = user_crud.get_by_email(db_session, "email@example.com")

        assert user is not None
        assert user.username == "emailuser"
        assert user.full_name == "Email User"

    def test_get_user_by_username(self, user_crud, db_session):
        """ユーザー名でのユーザー取得テスト"""
        user_data = UserTestData.create_user_data(
            email="username@example.com", username="usernameuser", full_name="Username User"
        )
        user_crud.create(db_session, obj_in=user_data)

        user = user_crud.get_by_username(db_session, "usernameuser")

        assert user is not None
        assert user.email == "username@example.com"
        assert user.full_name == "Username User"

    def test_get_users_with_pagination(self, user_crud, db_session):
        """ユーザー一覧取得（ページネーション）のテスト"""
        sample_users = UserTestData.create_sample_users()

        for user_data in sample_users:
            user_crud.create(db_session, obj_in=user_data)

        users = user_crud.get_multi(db_session, skip=0, limit=2)
        assert len(users) == 2

        users = user_crud.get_multi(db_session, skip=2, limit=1)
        assert len(users) == 1

    def test_get_active_users(self, user_crud, db_session):
        """アクティブユーザー一覧取得のテスト"""
        # アクティブユーザーを作成
        active_user_data = UserTestData.create_user_data(
            email="active@example.com", username="activeuser", full_name="Active User"
        )
        user_crud.create(db_session, obj_in=active_user_data)

        # 非アクティブユーザーを作成
        inactive_user_data = UserTestData.create_user_data(
            email="inactive@example.com", username="inactiveuser", full_name="Inactive User"
        )
        inactive_user = user_crud.create(db_session, obj_in=inactive_user_data)
        user_crud.deactivate(db_session, user_id=inactive_user.id)

        active_users = user_crud.get_active_users(db_session, skip=0, limit=10)
        assert len(active_users) == 1
        assert active_users[0].email == "active@example.com"

    def test_get_users_by_role(self, user_crud, db_session):
        """役割別ユーザー取得のテスト"""
        # 一般ユーザーを作成
        user_data = UserTestData.create_user_data(
            email="user@example.com", username="normaluser", full_name="Normal User", role="user"
        )
        user_crud.create(db_session, obj_in=user_data)

        # 管理者ユーザーを作成
        admin_data = UserTestData.create_user_data(
            email="admin@example.com", username="adminuser", full_name="Admin User", role="admin"
        )
        user_crud.create(db_session, obj_in=admin_data)

        admin_users = user_crud.get_by_role(db_session, "admin", skip=0, limit=10)
        assert len(admin_users) == 1
        assert admin_users[0].email == "admin@example.com"

    def test_update_user(self, user_crud, db_session):
        """ユーザー更新のテスト"""
        user_data = UserTestData.create_user_data(
            email="update@example.com", username="updateuser", full_name="Update User"
        )
        created_user = user_crud.create(db_session, obj_in=user_data)

        update_data = UserUpdate(full_name="Updated User", bio="Updated bio")
        updated_user = user_crud.update(db_session, user_id=created_user.id, obj_in=update_data)

        assert updated_user is not None
        assert updated_user.full_name == "Updated User"
        assert updated_user.bio == "Updated bio"
        assert updated_user.email == "update@example.com"  # 変更されていない

    def test_update_user_partial(self, user_crud, db_session):
        """ユーザーの部分更新テスト"""
        user_data = UserTestData.create_user_data(
            email="partial@example.com", username="partialuser", full_name="Partial User"
        )
        created_user = user_crud.create(db_session, obj_in=user_data)

        # 部分更新（bioのみ）
        update_data = UserUpdate(bio="New bio")
        updated_user = user_crud.update(db_session, user_id=created_user.id, obj_in=update_data)

        assert updated_user is not None
        assert updated_user.bio == "New bio"
        assert updated_user.full_name == "Partial User"  # 変更されていない
        assert updated_user.email == "partial@example.com"  # 変更されていない

    def test_update_password(self, user_crud, db_session):
        """パスワード更新のテスト"""
        user_data = UserTestData.create_user_data(
            email="password@example.com", username="passworduser", full_name="Password User"
        )
        created_user = user_crud.create(db_session, obj_in=user_data)

        new_hashed_password = "new_hashed_password_123"
        updated_user = user_crud.update_password(
            db_session, user_id=created_user.id, hashed_password=new_hashed_password
        )

        assert updated_user is not None
        assert updated_user.hashed_password == new_hashed_password

    def test_update_last_login(self, user_crud, db_session):
        """最終ログイン日時更新のテスト"""
        user_data = UserTestData.create_user_data(
            email="login@example.com", username="loginuser", full_name="Login User"
        )
        created_user = user_crud.create(db_session, obj_in=user_data)

        updated_user = user_crud.update_last_login(db_session, user_id=created_user.id)

        assert updated_user is not None
        assert updated_user.last_login is not None
        # ISO形式の日時文字列であることを確認
        datetime.fromisoformat(updated_user.last_login)

    def test_increment_failed_attempts(self, user_crud, db_session):
        """ログイン失敗回数増加のテスト"""
        user_data = UserTestData.create_user_data(
            email="failed@example.com", username="faileduser", full_name="Failed User"
        )
        created_user = user_crud.create(db_session, obj_in=user_data)

        # 初期状態は0
        assert created_user.failed_login_attempts == "0"

        # 失敗回数を増加
        updated_user = user_crud.increment_failed_attempts(db_session, user_id=created_user.id)
        assert updated_user.failed_login_attempts == "1"

        # さらに増加
        updated_user = user_crud.increment_failed_attempts(db_session, user_id=created_user.id)
        assert updated_user.failed_login_attempts == "2"

    def test_reset_failed_attempts(self, user_crud, db_session):
        """ログイン失敗回数リセットのテスト"""
        user_data = UserTestData.create_user_data(
            email="reset@example.com", username="resetuser", full_name="Reset User"
        )
        created_user = user_crud.create(db_session, obj_in=user_data)

        # 失敗回数を増加
        user_crud.increment_failed_attempts(db_session, user_id=created_user.id)
        user_crud.increment_failed_attempts(db_session, user_id=created_user.id)

        # リセット
        updated_user = user_crud.reset_failed_attempts(db_session, user_id=created_user.id)
        assert updated_user.failed_login_attempts == "0"
        assert updated_user.locked_until is None

    def test_lock_account(self, user_crud, db_session):
        """アカウントロックのテスト"""
        user_data = UserTestData.create_user_data(email="lock@example.com", username="lockuser", full_name="Lock User")
        created_user = user_crud.create(db_session, obj_in=user_data)

        # アカウントをロック
        updated_user = user_crud.lock_account(db_session, user_id=created_user.id, lock_minutes=30)

        assert updated_user is not None
        assert updated_user.locked_until is not None
        # ロック期限が未来であることを確認
        lock_time = datetime.fromisoformat(updated_user.locked_until)
        assert lock_time > datetime.now(timezone.utc)

    def test_unlock_account(self, user_crud, db_session):
        """アカウントロック解除のテスト"""
        user_data = UserTestData.create_user_data(
            email="unlock@example.com", username="unlockuser", full_name="Unlock User"
        )
        created_user = user_crud.create(db_session, obj_in=user_data)

        # アカウントをロック
        user_crud.lock_account(db_session, user_id=created_user.id, lock_minutes=30)

        # ロックを解除
        updated_user = user_crud.unlock_account(db_session, user_id=created_user.id)
        assert updated_user.locked_until is None

    def test_deactivate_user(self, user_crud, db_session):
        """ユーザー無効化のテスト"""
        user_data = UserTestData.create_user_data(
            email="deactivate@example.com", username="deactivateuser", full_name="Deactivate User"
        )
        created_user = user_crud.create(db_session, obj_in=user_data)

        # 初期状態はアクティブ
        assert created_user.is_active is True

        # 無効化
        updated_user = user_crud.deactivate(db_session, user_id=created_user.id)
        assert updated_user.is_active is False

    def test_activate_user(self, user_crud, db_session):
        """ユーザー有効化のテスト"""
        user_data = UserTestData.create_user_data(
            email="activate@example.com", username="activateuser", full_name="Activate User"
        )
        created_user = user_crud.create(db_session, obj_in=user_data)

        # 無効化
        user_crud.deactivate(db_session, user_id=created_user.id)

        # 有効化
        updated_user = user_crud.activate(db_session, user_id=created_user.id)
        assert updated_user.is_active is True

    def test_delete_user(self, user_crud, db_session):
        """ユーザー削除のテスト"""
        user_data = UserTestData.create_user_data(
            email="delete@example.com", username="deleteuser", full_name="Delete User"
        )
        created_user = user_crud.create(db_session, obj_in=user_data)

        success = user_crud.remove(db_session, user_id=created_user.id)
        assert success is True

        deleted_user = user_crud.get(db_session, created_user.id)
        assert deleted_user is None

    def test_exists_user(self, user_crud, db_session):
        """ユーザー存在確認のテスト"""
        user_data = UserTestData.create_user_data(
            email="exists@example.com", username="existsuser", full_name="Exists User"
        )
        user_crud.create(db_session, obj_in=user_data)

        # メールアドレスでの存在確認
        assert user_crud.exists(db_session, email="exists@example.com") is True
        assert user_crud.exists(db_session, email="nonexistent@example.com") is False

        # ユーザー名での存在確認
        assert user_crud.exists(db_session, username="existsuser") is True
        assert user_crud.exists(db_session, username="nonexistentuser") is False

    def test_count_users(self, user_crud, db_session):
        """ユーザー数取得のテスト"""
        # 初期状態
        assert user_crud.count(db_session) == 0

        # ユーザーを作成
        sample_users = UserTestData.create_sample_users()
        for user_data in sample_users:
            user_crud.create(db_session, obj_in=user_data)

        assert user_crud.count(db_session) == 3

    def test_count_active_users(self, user_crud, db_session):
        """アクティブユーザー数取得のテスト"""
        # アクティブユーザーを作成
        active_user_data = UserTestData.create_user_data(
            email="active_count@example.com", username="activecountuser", full_name="Active Count User"
        )
        user_crud.create(db_session, obj_in=active_user_data)

        # 非アクティブユーザーを作成
        inactive_user_data = UserTestData.create_user_data(
            email="inactive_count@example.com", username="inactivecountuser", full_name="Inactive Count User"
        )
        inactive_user = user_crud.create(db_session, obj_in=inactive_user_data)
        user_crud.deactivate(db_session, user_id=inactive_user.id)

        assert user_crud.count_active(db_session) == 1

    def test_count_by_role(self, user_crud, db_session):
        """役割別ユーザー数取得のテスト"""
        # 一般ユーザーを作成
        user_data = UserTestData.create_user_data(
            email="role_count@example.com", username="rolecountuser", full_name="Role Count User", role="user"
        )
        user_crud.create(db_session, obj_in=user_data)

        # 管理者ユーザーを作成
        admin_data = UserTestData.create_user_data(
            email="admin_count@example.com", username="admincountuser", full_name="Admin Count User", role="admin"
        )
        user_crud.create(db_session, obj_in=admin_data)

        assert user_crud.count_by_role(db_session, "user") == 1
        assert user_crud.count_by_role(db_session, "admin") == 1
        assert user_crud.count_by_role(db_session, "moderator") == 0

    def test_get_user_not_found(self, user_crud, db_session):
        """存在しないユーザーの取得テスト"""
        user = user_crud.get(db_session, "non-existent-id")
        assert user is None

    def test_get_user_by_email_not_found(self, user_crud, db_session):
        """存在しないメールアドレスでのユーザー取得テスト"""
        user = user_crud.get_by_email(db_session, "nonexistent@example.com")
        assert user is None

    def test_get_user_by_username_not_found(self, user_crud, db_session):
        """存在しないユーザー名でのユーザー取得テスト"""
        user = user_crud.get_by_username(db_session, "nonexistentuser")
        assert user is None

    def test_update_user_not_found(self, user_crud, db_session):
        """存在しないユーザーの更新テスト"""
        update_data = UserUpdate(full_name="Updated User")
        updated_user = user_crud.update(db_session, user_id="non-existent-id", obj_in=update_data)
        assert updated_user is None

    def test_delete_user_not_found(self, user_crud, db_session):
        """存在しないユーザーの削除テスト"""
        success = user_crud.remove(db_session, user_id="non-existent-id")
        assert success is False

    def test_update_with_none_values(self, user_crud, db_session):
        """None値を含む更新テスト"""
        user_data = UserTestData.create_user_data(
            email="none@example.com", username="noneuser", full_name="None User", bio="Original bio"
        )
        created_user = user_crud.create(db_session, obj_in=user_data)

        print("before update: bio=", created_user.bio)

        # None値を含む更新データ（現在の実装ではNone値は除外される）
        update_data = UserUpdate(bio=None, avatar_url=None)
        print("update_data.model_dump(exclude_unset=True)=", update_data.model_dump(exclude_unset=True))
        print("update_data.model_dump()=", update_data.model_dump())

        updated_user = user_crud.update(db_session, user_id=created_user.id, obj_in=update_data)

        print("after update: bio=", updated_user.bio)

        assert updated_user is not None
        # Pydantic v2では明示的にNoneを渡すとNoneで上書きされるのが正しい挙動
        assert updated_user.bio is None  # Noneで上書きされる
        assert updated_user.avatar_url is None  # 元々Noneなので変更されない
