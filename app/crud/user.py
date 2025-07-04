"""
CRUD operations for User entity.

This module provides data access layer operations for the user table.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from .. import schemas
from ..auth.utils import get_password_hash
from ..models.user import User


class UserCRUD:
    """
    ユーザーCRUDクラス

    ユーザーエンティティの全てのデータアクセス操作を提供します。
    """

    def get(self, db: Session, user_id: str) -> Optional[User]:
        """IDでユーザーを取得"""
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """メールアドレスでユーザーを取得"""
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """ユーザー名でユーザーを取得"""
        return db.query(User).filter(User.username == username).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """ユーザー一覧を取得"""
        return db.query(User).offset(skip).limit(limit).all()

    def get_active_users(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """アクティブユーザー一覧を取得"""
        return db.query(User).filter(User.is_active.is_(True)).offset(skip).limit(limit).all()

    def get_by_role(self, db: Session, role: str, *, skip: int = 0, limit: int = 100) -> List[User]:
        """役割でユーザーを検索"""
        return db.query(User).filter(User.role == role).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: schemas.UserCreate) -> User:
        """ユーザーを作成"""
        data = obj_in.model_dump()
        password = data.pop("password", None)
        if password:
            data["hashed_password"] = get_password_hash(password)
        db_user = User(**data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update(self, db: Session, *, user_id: str, obj_in: schemas.UserUpdate) -> Optional[User]:
        """ユーザーを更新"""
        db_user = self.get(db, user_id)
        if db_user:
            # exclude_unset=True で「リクエストで明示的に値が渡されたフィールドのみ」取得
            update_data = obj_in.model_dump(exclude_unset=True)

            # 更新対象フィールドを設定（None値も含める）
            for field, value in update_data.items():
                setattr(db_user, field, value)

            db.commit()
            db.refresh(db_user)
        return db_user

    def update_password(self, db: Session, *, user_id: str, hashed_password: str) -> Optional[User]:
        """パスワードを更新"""
        db_user = self.get(db, user_id)
        if db_user:
            db_user.hashed_password = hashed_password
            db.commit()
            db.refresh(db_user)
        return db_user

    def update_last_login(self, db: Session, *, user_id: str) -> Optional[User]:
        """最終ログイン日時を更新"""
        db_user = self.get(db, user_id)
        if db_user:
            from datetime import datetime

            db_user.last_login = datetime.utcnow().isoformat()
            db.commit()
            db.refresh(db_user)
        return db_user

    def increment_failed_attempts(self, db: Session, *, user_id: str) -> Optional[User]:
        """ログイン失敗回数を増加"""
        db_user = self.get(db, user_id)
        if db_user:
            current_count = int(db_user.failed_login_attempts or "0")
            db_user.failed_login_attempts = str(current_count + 1)
            db.commit()
            db.refresh(db_user)
        return db_user

    def reset_failed_attempts(self, db: Session, *, user_id: str) -> Optional[User]:
        """ログイン失敗回数をリセット"""
        db_user = self.get(db, user_id)
        if db_user:
            db_user.failed_login_attempts = "0"
            db_user.locked_until = None
            db.commit()
            db.refresh(db_user)
        return db_user

    def lock_account(self, db: Session, *, user_id: str, lock_minutes: int = 30) -> Optional[User]:
        """アカウントをロック"""
        db_user = self.get(db, user_id)
        if db_user:
            from datetime import datetime, timedelta

            lock_time = datetime.utcnow() + timedelta(minutes=lock_minutes)
            db_user.locked_until = lock_time.isoformat()
            db.commit()
            db.refresh(db_user)
        return db_user

    def unlock_account(self, db: Session, *, user_id: str) -> Optional[User]:
        """アカウントのロックを解除"""
        db_user = self.get(db, user_id)
        if db_user:
            db_user.locked_until = None
            db.commit()
            db.refresh(db_user)
        return db_user

    def deactivate(self, db: Session, *, user_id: str) -> Optional[User]:
        """ユーザーを無効化"""
        db_user = self.get(db, user_id)
        if db_user:
            db_user.is_active = False
            db.commit()
            db.refresh(db_user)
        return db_user

    def activate(self, db: Session, *, user_id: str) -> Optional[User]:
        """ユーザーを有効化"""
        db_user = self.get(db, user_id)
        if db_user:
            db_user.is_active = True
            db.commit()
            db.refresh(db_user)
        return db_user

    def remove(self, db: Session, *, user_id: str) -> bool:
        """ユーザーを削除"""
        db_user = self.get(db, user_id)
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False

    def exists(self, db: Session, *, email: Optional[str] = None, username: Optional[str] = None) -> bool:
        """ユーザーの存在確認"""
        if email:
            return db.query(User).filter(User.email == email).first() is not None
        if username:
            return db.query(User).filter(User.username == username).first() is not None
        return False

    def count(self, db: Session) -> int:
        """ユーザー数を取得"""
        return db.query(User).count()

    def count_active(self, db: Session) -> int:
        """アクティブユーザー数を取得"""
        return db.query(User).filter(User.is_active.is_(True)).count()

    def count_by_role(self, db: Session, role: str) -> int:
        """役割別ユーザー数を取得"""
        return db.query(User).filter(User.role == role).count()


# シングルトンインスタンス
user_crud = UserCRUD()
