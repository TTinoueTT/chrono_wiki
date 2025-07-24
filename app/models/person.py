from sqlalchemy import Column, Date, String, Text, event
from sqlalchemy.orm import relationship

from .base import BaseModel


class Person(BaseModel):
    """人物モデル"""

    __tablename__ = "person"

    # idはBaseModelで定義済みのため削除
    ssid = Column(String(50), nullable=False, unique=True, index=True)
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
    tags = relationship("Tag", secondary="person_tag", back_populates="persons")
    events = relationship("Event", secondary="event_person", back_populates="persons")

    def generate_search_name(self):
        """search_nameを自動生成"""
        parts = [
            str(self.ssid or ""),
            str(self.display_name or ""),
            str(self.full_name or ""),
            str(self.born_country or ""),
            str(self.born_region or ""),
        ]
        return " ".join(parts).lower()


# イベントリスナー
@event.listens_for(Person, "before_insert")
@event.listens_for(Person, "before_update")
def generate_search_name(mapper, connection, target):
    """Person作成・更新時にsearch_nameを自動生成"""
    target.search_name = target.generate_search_name()
