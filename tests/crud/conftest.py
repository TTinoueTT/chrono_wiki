"""
Common test utilities and fixtures for CRUD tests.
"""

import os
from datetime import date
from typing import Optional

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base

# テスト用PostgreSQL設定
SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("TEST_DATABASE_URL environment variable is required")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="function")
def db_session():
    """テスト用データベースセッション"""
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


# テストデータファクトリ
class PersonTestData:
    """人物テストデータファクトリ"""

    @staticmethod
    def create_person_data(
        ssid: str = "test_person_001",
        full_name: str = "織田信長",
        display_name: str = "信長",
        search_name: str = "おだのぶなが",
        birth_date: str = "1534-06-23",
        death_date: Optional[str] = "1582-06-21",
        born_country: str = "日本",
        born_region: str = "尾張国",
        description: str = "戦国時代の武将",
        portrait_url: Optional[str] = "https://example.com/nobunaga.jpg",
    ):
        """人物テストデータを作成"""
        from app.schemas import PersonCreate

        # 文字列をdate型に変換
        birth_date_obj = date.fromisoformat(birth_date)
        death_date_obj = date.fromisoformat(death_date) if death_date else None

        return PersonCreate(
            ssid=ssid,
            full_name=full_name,
            display_name=display_name,
            search_name=search_name,
            birth_date=birth_date_obj,
            death_date=death_date_obj,
            born_country=born_country,
            born_region=born_region,
            description=description,
            portrait_url=portrait_url,
        )

    @staticmethod
    def create_sample_persons():
        """サンプル人物データを作成"""
        return [
            PersonTestData.create_person_data(
                ssid="test_person_001",
                full_name="織田信長",
                display_name="信長",
                search_name="おだのぶなが",
                birth_date="1534-06-23",
                death_date="1582-06-21",
                born_country="日本",
                born_region="尾張国",
                description="戦国時代の武将",
            ),
            PersonTestData.create_person_data(
                ssid="test_person_002",
                full_name="豊臣秀吉",
                display_name="秀吉",
                search_name="とよとみひでよし",
                birth_date="1537-03-17",
                death_date="1598-09-18",
                born_country="日本",
                born_region="尾張国",
                description="天下統一を果たした武将",
            ),
            PersonTestData.create_person_data(
                ssid="test_person_003",
                full_name="徳川家康",
                display_name="家康",
                search_name="とくがわいえやす",
                birth_date="1543-01-31",
                death_date="1616-06-01",
                born_country="日本",
                born_region="三河国",
                description="江戸幕府を開いた武将",
            ),
        ]


class TagTestData:
    """タグテストデータファクトリ"""

    @staticmethod
    def create_tag_data(
        ssid: str = "test_tag_001",
        name: str = "戦国武将",
        description: str = "戦国時代の武将",
    ):
        """タグテストデータを作成"""
        from app.schemas import TagCreate

        return TagCreate(ssid=ssid, name=name, description=description)

    @staticmethod
    def create_sample_tags():
        """サンプルタグデータを作成"""
        return [
            TagTestData.create_tag_data(
                ssid="test_tag_001",
                name="戦国武将",
                description="戦国時代の武将",
            ),
            TagTestData.create_tag_data(
                ssid="test_tag_002", name="大名", description="地方の支配者"
            ),
            TagTestData.create_tag_data(
                ssid="test_tag_003", name="軍師", description="戦略を立てる者"
            ),
        ]


class EventTestData:
    """イベントテストデータファクトリ"""

    @staticmethod
    def create_event_data(
        ssid: str = "test_event_001",
        title: str = "桶狭間の戦い",
        start_date: str = "1560-06-12",
        end_date: Optional[str] = "1560-06-12",
        description: str = "織田信長が今川義元を破った戦い",
        location_name: str = "桶狭間",
        latitude: float = 35.123456,
        longitude: float = 136.789012,
        place_id: Optional[str] = None,
        image_url: Optional[dict] = None,
    ):
        """イベントテストデータを作成"""
        from app.schemas import EventCreate

        # 文字列をdate型に変換
        start_date_obj = date.fromisoformat(start_date)
        end_date_obj = date.fromisoformat(end_date) if end_date else None

        return EventCreate(
            ssid=ssid,
            title=title,
            start_date=start_date_obj,
            end_date=end_date_obj,
            description=description,
            location_name=location_name,
            latitude=latitude,
            longitude=longitude,
            place_id=place_id,
            image_url=image_url,
        )

    @staticmethod
    def create_sample_events():
        """サンプルイベントデータを作成"""
        return [
            EventTestData.create_event_data(
                ssid="test_event_001",
                title="桶狭間の戦い",
                start_date="1560-06-12",
                end_date="1560-06-12",
                description="織田信長が今川義元を破った戦い",
                location_name="桶狭間",
            ),
            EventTestData.create_event_data(
                ssid="test_event_002",
                title="本能寺の変",
                start_date="1582-06-21",
                end_date="1582-06-21",
                description="織田信長が明智光秀に討たれた事件",
                location_name="本能寺",
            ),
            EventTestData.create_event_data(
                ssid="test_event_003",
                title="関ヶ原の戦い",
                start_date="1600-10-21",
                end_date="1600-10-21",
                description="徳川家康が石田三成を破った戦い",
                location_name="関ヶ原",
            ),
        ]
