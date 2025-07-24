"""
ユーザーサービス層

ビジネスロジックを担当し、CRUD層とルーター層の間の橋渡しをします。
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from .. import schemas
from ..crud.user import user_crud
from ..models.user import User


class UserService:
    """ユーザーサービスクラス"""

    def create_user(self, db: Session, user_data: schemas.UserCreate) -> User:
        """ユーザーを作成"""
        # メールアドレス重複チェック
        if user_crud.exists(db, email=user_data.email):
            raise ValueError("Email already registered")

        # ユーザー名重複チェック
        if user_crud.exists(db, username=user_data.username):
            raise ValueError("Username already taken")

        return user_crud.create(db, obj_in=user_data)

    def get_user(self, db: Session, user_id: str) -> Optional[User]:
        """ユーザーを取得"""
        return user_crud.get(db, user_id)

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """メールアドレスでユーザーを取得"""
        return user_crud.get_by_email(db, email)

    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """ユーザー名でユーザーを取得"""
        return user_crud.get_by_username(db, username)

    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """ユーザー一覧を取得"""
        return user_crud.get_multi(db, skip=skip, limit=limit)

    def get_active_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """アクティブユーザー一覧を取得"""
        return user_crud.get_active_users(db, skip=skip, limit=limit)

    def get_users_by_role(self, db: Session, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """役割でユーザーを検索"""
        return user_crud.get_by_role(db, role, skip=skip, limit=limit)

    def update_user(self, db: Session, user_id: str, user_data: schemas.UserUpdate) -> Optional[User]:
        """ユーザーを更新"""
        # ユーザーが存在するかチェック
        existing_user = user_crud.get(db, user_id)
        if not existing_user:
            return None

        # メールアドレス変更時の重複チェック
        if user_data.email and user_data.email != existing_user.email:
            if user_crud.exists(db, email=user_data.email):
                raise ValueError("Email already registered")

        # ユーザー名変更時の重複チェック
        if user_data.username and user_data.username != existing_user.username:
            if user_crud.exists(db, username=user_data.username):
                raise ValueError("Username already taken")

        return user_crud.update(db, user_id=user_id, obj_in=user_data)

    def update_password(self, db: Session, user_id: str, new_password: str) -> Optional[User]:
        """パスワードを更新"""
        from ..auth.utils import get_password_hash

        hashed_password = get_password_hash(new_password)
        return user_crud.update_password(db, user_id=user_id, hashed_password=hashed_password)

    def update_last_login(self, db: Session, user_id: str) -> Optional[User]:
        """最終ログイン日時を更新"""
        return user_crud.update_last_login(db, user_id=user_id)

    def increment_failed_attempts(self, db: Session, user_id: str) -> Optional[User]:
        """ログイン失敗回数を増加"""
        return user_crud.increment_failed_attempts(db, user_id=user_id)

    def reset_failed_attempts(self, db: Session, user_id: str) -> Optional[User]:
        """ログイン失敗回数をリセット"""
        return user_crud.reset_failed_attempts(db, user_id=user_id)

    def lock_account(self, db: Session, user_id: str, lock_minutes: int = 30) -> Optional[User]:
        """アカウントをロック"""
        return user_crud.lock_account(db, user_id=user_id, lock_minutes=lock_minutes)

    def unlock_account(self, db: Session, user_id: str) -> Optional[User]:
        """アカウントのロックを解除"""
        return user_crud.unlock_account(db, user_id=user_id)

    def deactivate_user(self, db: Session, user_id: str) -> Optional[User]:
        """ユーザーを無効化"""
        return user_crud.deactivate(db, user_id=user_id)

    def activate_user(self, db: Session, user_id: str) -> Optional[User]:
        """ユーザーを有効化"""
        return user_crud.activate(db, user_id=user_id)

    def delete_user(self, db: Session, user_id: str) -> bool:
        """ユーザーを削除"""
        return user_crud.remove(db, user_id=user_id)

    def exists_user(self, db: Session, email: Optional[str] = None, username: Optional[str] = None) -> bool:
        """ユーザーの存在確認"""
        return user_crud.exists(db, email=email, username=username)

    def count_users(self, db: Session) -> int:
        """ユーザー数を取得"""
        return user_crud.count(db)

    def count_active_users(self, db: Session) -> int:
        """アクティブユーザー数を取得"""
        return user_crud.count_active(db)

    def count_users_by_role(self, db: Session, role: str) -> int:
        """役割別ユーザー数を取得"""
        return user_crud.count_by_role(db, role)


# シングルトンインスタンス
user_service = UserService()
