from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class Tag(BaseModel):
    """タグモデル"""

    __tablename__ = "tag"

    # idはBaseModelで定義済みのため削除
    ssid = Column(String(50), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)

    # リレーションシップ
    persons = relationship(
        "Person", secondary="person_tag", back_populates="tags"
    )
    events = relationship(
        "Event", secondary="event_tag", back_populates="tags"
    )
