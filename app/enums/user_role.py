"""
ユーザーロールを定義するEnum

認証・認可システムで使用するユーザーロールを管理します。
"""

from enum import Enum


class UserRole(str, Enum):
    """ユーザーロール"""

    PUBLIC = "public"  # 未認証ユーザー（閲覧のみ）
    USER = "user"  # 一般ユーザー
    MODERATOR = "moderator"  # モデレーター
    ADMIN = "admin"  # 管理者

    @classmethod
    def get_display_name(cls, role: str) -> str:
        """ロールの表示名を取得"""
        try:
            return cls(role).value
        except ValueError:
            return role

    @classmethod
    def get_choices(cls) -> list[tuple[str, str]]:
        """選択肢のリストを取得（フォーム用）"""
        return [(role.value, role.value) for role in cls]

    @classmethod
    def is_valid(cls, role: str) -> bool:
        """ロールが有効かチェック"""
        return role in [r.value for r in cls]

    @classmethod
    def get_hierarchy_level(cls, role: str) -> int:
        """ロールの階層レベルを取得（数値が大きいほど権限が高い）"""
        hierarchy = {
            cls.PUBLIC.value: 0,
            cls.USER.value: 1,
            cls.MODERATOR.value: 2,
            cls.ADMIN.value: 3,
        }
        return hierarchy.get(role, 0)

    @classmethod
    def has_permission(cls, user_role: str, required_role: str) -> bool:
        """ユーザーロールが指定されたロール以上の権限を持っているかチェック"""
        user_level = cls.get_hierarchy_level(user_role)
        required_level = cls.get_hierarchy_level(required_role)
        return user_level >= required_level
