from sqlalchemy import BigInteger, Column, ForeignKey, String

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
