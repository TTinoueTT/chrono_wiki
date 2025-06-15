from sqlalchemy import JSON, BigInteger, Column, Date, Numeric, String, Text
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Event(Base, TimestampMixin):
    """出来事モデル"""
    __tablename__ = "event"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ssid = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    start_data = Column(Date, nullable=False)
    end_data = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    location_name = Column(String(255), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    place_id = Column(String(255), nullable=True)
    image_url = Column(JSON, nullable=True)

    # リレーションシップ
    tags = relationship(
        "Tag",
        secondary="event_tag",
        back_populates="events"
    )
    persons = relationship(
        "Person",
        secondary="event_person",
        back_populates="events"
    )
