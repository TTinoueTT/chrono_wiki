import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app
from app.models.base import Base

# テスト用PostgreSQL設定
SQLALCHEMY_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://test_user:test_password@localhost:5433/test_historical_figures",
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False,  # テスト時はSQLログを無効化
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def override_get_db():
    """テスト用のデータベースセッション"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    """テスト用データベースのセットアップ"""
    # テーブルを作成
    Base.metadata.create_all(bind=engine)

    yield

    # テスト後にテーブルを削除
    Base.metadata.drop_all(bind=engine)


class TestPersonsAPI:
    """人物APIのテスト"""

    def test_create_person(self, setup_database):
        """人物作成のテスト"""
        person_data = {
            "ssid": "test_person_001",
            "full_name": "織田信長",
            "display_name": "信長",
            "search_name": "おだのぶなが",
            "birth_date": "1534-06-23",
            "death_date": "1582-06-21",
            "born_country": "日本",
            "born_region": "尾張国",
            "description": "戦国時代の武将",
            "portrait_url": "https://example.com/nobunaga.jpg",
        }

        response = client.post("/persons/", json=person_data)
        assert response.status_code == 201
        data = response.json()
        assert data["ssid"] == person_data["ssid"]
        assert data["full_name"] == person_data["full_name"]
        assert "id" in data

    def test_get_persons(self, setup_database):
        """人物一覧取得のテスト"""
        # テストデータ作成
        person_data = {
            "ssid": "test_person_002",
            "full_name": "豊臣秀吉",
            "display_name": "秀吉",
            "search_name": "とよとみひでよし",
            "birth_date": "1537-03-17",
            "death_date": "1598-09-18",
            "born_country": "日本",
            "born_region": "尾張国",
            "description": "天下統一を果たした武将",
        }
        client.post("/persons/", json=person_data)

        response = client.get("/persons/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["full_name"] == "豊臣秀吉"

    def test_get_person_by_id(self, setup_database):
        """ID指定での人物取得テスト"""
        # テストデータ作成
        person_data = {
            "ssid": "test_person_003",
            "full_name": "徳川家康",
            "display_name": "家康",
            "search_name": "とくがわいえやす",
            "birth_date": "1543-01-31",
            "death_date": "1616-06-01",
            "born_country": "日本",
            "born_region": "三河国",
            "description": "江戸幕府を開いた武将",
        }
        create_response = client.post("/persons/", json=person_data)
        person_id = create_response.json()["id"]

        response = client.get(f"/persons/{person_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "徳川家康"

    def test_update_person(self, setup_database):
        """人物更新のテスト"""
        # テストデータ作成
        person_data = {
            "ssid": "test_person_004",
            "full_name": "武田信玄",
            "display_name": "信玄",
            "search_name": "たけだしんげん",
            "birth_date": "1521-12-01",
            "death_date": "1573-05-13",
            "born_country": "日本",
            "born_region": "甲斐国",
            "description": "甲斐の虎",
        }
        create_response = client.post("/persons/", json=person_data)
        person_id = create_response.json()["id"]

        # 更新データ
        update_data = {"description": "甲斐の虎、風林火山"}

        response = client.put(f"/persons/{person_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "甲斐の虎、風林火山"

    def test_delete_person(self, setup_database):
        """人物削除のテスト"""
        # テストデータ作成
        person_data = {
            "ssid": "test_person_005",
            "full_name": "上杉謙信",
            "display_name": "謙信",
            "search_name": "うえすぎけんしん",
            "birth_date": "1530-02-18",
            "death_date": "1578-04-19",
            "born_country": "日本",
            "born_region": "越後国",
            "description": "越後の龍",
        }
        create_response = client.post("/persons/", json=person_data)
        person_id = create_response.json()["id"]

        # 削除実行
        response = client.delete(f"/persons/{person_id}")
        assert response.status_code == 204

        # 削除確認
        get_response = client.get(f"/persons/{person_id}")
        assert get_response.status_code == 404


class TestTagsAPI:
    """タグAPIのテスト"""

    def test_create_tag(self, setup_database):
        """タグ作成のテスト"""
        tag_data = {
            "ssid": "test_tag_001",
            "name": "戦国武将",
            "description": "戦国時代の武将",
        }

        response = client.post("/tags/", json=tag_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == tag_data["name"]

    def test_get_tags(self, setup_database):
        """タグ一覧取得のテスト"""
        response = client.get("/tags/")
        assert response.status_code == 200


class TestEventsAPI:
    """イベントAPIのテスト"""

    def test_create_event(self, setup_database):
        """イベント作成のテスト"""
        event_data = {
            "ssid": "test_event_001",
            "title": "桶狭間の戦い",
            "start_date": "1560-06-12",
            "end_date": "1560-06-12",
            "description": "織田信長が今川義元を破った戦い",
            "location_name": "桶狭間",
            "latitude": 35.123456,
            "longitude": 136.789012,
        }

        response = client.post("/events/", json=event_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == event_data["title"]

    def test_get_events(self, setup_database):
        """イベント一覧取得のテスト"""
        response = client.get("/events/")
        assert response.status_code == 200
