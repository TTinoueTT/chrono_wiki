from sqlalchemy import BigInteger, Column, ForeignKey, String

from ..enums import EventPersonRole
from .base import Base, TimestampMixin


# 人物とタグの中間テーブル
class PersonTag(Base, TimestampMixin):
    """人物とタグの中間テーブル"""

    __tablename__ = "person_tag"

    person_id = Column(BigInteger, ForeignKey("person.id"), primary_key=True)
    tag_id = Column(BigInteger, ForeignKey("tag.id"), primary_key=True)


# 出来事とタグの中間テーブル
class EventTag(Base, TimestampMixin):
    """出来事とタグの中間テーブル"""

    __tablename__ = "event_tag"

    event_id = Column(BigInteger, ForeignKey("event.id"), primary_key=True)
    tag_id = Column(BigInteger, ForeignKey("tag.id"), primary_key=True)


# 出来事と人物の中間テーブル
class EventPerson(Base, TimestampMixin):
    """出来事と人物の中間テーブル"""

    __tablename__ = "event_person"

    event_id = Column(BigInteger, ForeignKey("event.id"), primary_key=True)
    person_id = Column(BigInteger, ForeignKey("person.id"), primary_key=True)
    role = Column(String(50), nullable=True)

    def set_role(self, role: EventPersonRole) -> None:
        """役割を設定（Enum使用）"""
        setattr(self, "role", role.value)

    def get_role(self) -> EventPersonRole:
        """役割を取得（Enumとして）"""
        role_value = getattr(self, "role", None)
        if role_value:
            try:
                return EventPersonRole(role_value)
            except ValueError:
                return EventPersonRole.OTHER
        return EventPersonRole.OTHER

    @property
    def role_display(self) -> str:
        """役割の表示名を取得"""
        return self.get_role().value
