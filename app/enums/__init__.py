"""
Enum定義

アプリケーション全体で使用する列挙型を定義します。
"""

from .event_person_role import EventPersonRole
from .user_role import UserRole

__all__ = [
    "EventPersonRole",
    "UserRole",
]
