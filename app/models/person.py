from sqlalchemy import BigInteger, Column, Date, String, Text
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Person(Base, TimestampMixin):
    """人物モデル"""
    __tablename__ = "person"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ssid = Column(String(50), nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    display_name = Column(String(50), nullable=False)
    search_name = Column(String(255), nullable=False, index=True)
    birth_date = Column(Date, nullable=False)
    death_date = Column(Date, nullable=True)
    born_country = Column(String(100), nullable=False)
    born_region = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    portrait_url = Column(String(2048), nullable=True)

    # リレーションシップ
    tags = relationship(
        "Tag",
        secondary="person_tag",
        back_populates="persons"
    )
    events = relationship(
        "Event",
        secondary="event_person",
        back_populates="persons"
    )
