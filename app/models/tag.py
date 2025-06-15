from sqlalchemy import BigInteger, Column, String, Text
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Tag(Base, TimestampMixin):
    """タグモデル"""
    __tablename__ = "tag"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ssid = Column(String(50), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)

    # リレーションシップ
    persons = relationship(
        "Person",
        secondary="person_tag",
        back_populates="tags"
    )
    events = relationship(
        "Event",
        secondary="event_tag",
        back_populates="tags"
    )
