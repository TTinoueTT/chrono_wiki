"""
ルーター層テスト用のフィクスチャ

ルーター層のテストに必要な共通フィクスチャを定義します。
"""

import os
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.dependencies.authorization import verify_token
from app.main import app
from app.models.base import Base
from app.services import EventService, PersonService, TagService


# テスト用の環境変数を設定
@pytest.fixture(autouse=True)
def setup_test_env():
    """テスト用の環境変数を設定"""
    # PostgreSQL 17を使用したテスト環境
    test_db_url = os.getenv("TEST_DATABASE_URL")
    if not test_db_url:
        raise ValueError("TEST_DATABASE_URL environment variable is required for tests")

    os.environ["DATABASE_URL"] = test_db_url
    os.environ["TEST_DATABASE_URL"] = test_db_url
    yield
    # テスト後のクリーンアップは不要（テストDBは独立）


@pytest.fixture
def test_engine():
    """テスト用のデータベースエンジン"""
    test_db_url = os.getenv("TEST_DATABASE_URL")
    if not test_db_url:
        raise ValueError("TEST_DATABASE_URL environment variable is required for tests")

    engine = create_engine(test_db_url)

    # テーブルを作成
    Base.metadata.create_all(bind=engine)

    yield engine

    # テスト後にテーブルを削除
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_session_factory(test_engine):
    """テスト用のセッションファクトリ"""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def test_db_session(test_session_factory):
    """テスト用のデータベースセッション"""
    session = test_session_factory()
    try:
        yield session
    finally:
        session.close()


def mock_verify_token():
    """テスト用の認証バイパス関数"""
    return {"auth_type": "api_key", "scope": "global", "test_mode": True}


@pytest.fixture
def client(test_db_session):
    """FastAPIテストクライアント（実際のDB使用）"""

    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    # データベース依存性をオーバーライド
    app.dependency_overrides[get_db] = override_get_db

    # 認証依存性をオーバーライド（テスト用）
    app.dependency_overrides[verify_token] = mock_verify_token

    yield TestClient(app)

    # クリーンアップ
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client(test_db_session):
    """認証付きFastAPIテストクライアント（実際のAPIキー使用）"""

    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    # データベース依存性をオーバーライド
    app.dependency_overrides[get_db] = override_get_db

    # 実際のAPIキーを使用
    api_key = os.getenv("API_KEY", "dev_sk_default")

    yield TestClient(app, headers={"Authorization": api_key})

    # クリーンアップ
    app.dependency_overrides.clear()


@pytest.fixture
def mock_person_service():
    """人物サービスのモック"""
    return Mock(spec=PersonService)


@pytest.fixture
def mock_event_service():
    """イベントサービスのモック"""
    return Mock(spec=EventService)


@pytest.fixture
def mock_tag_service():
    """タグサービスのモック"""
    return Mock(spec=TagService)


@pytest.fixture
def mock_db_session():
    """データベースセッションのモック"""
    return Mock()


# テスト用のサンプルデータ
@pytest.fixture
def sample_person_data():
    """テスト用の人物データ"""
    return {
        "ssid": "test_person_001",
        "full_name": "織田信長",
        "display_name": "信長",
        "birth_date": "1534-06-23",
        "death_date": "1582-06-21",
        "born_country": "日本",
        "born_region": "尾張国",
        "description": "戦国時代の武将",
    }


@pytest.fixture
def sample_person_response():
    """テスト用の人物レスポンスデータ"""
    return {
        "id": 1,
        "ssid": "test_person_001",
        "full_name": "織田信長",
        "display_name": "信長",
        "birth_date": "1534-06-23",
        "death_date": "1582-06-21",
        "born_country": "日本",
        "born_region": "尾張国",
        "description": "戦国時代の武将",
        "portrait_url": None,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }


@pytest.fixture
def sample_event_data():
    """テスト用のイベントデータ"""
    return {
        "ssid": "test_event_001",
        "title": "桶狭間の戦い",
        "start_date": "1560-05-19",
        "end_date": "1560-05-19",
        "description": "織田信長が今川義元を破った戦い",
        "location_name": "桶狭間",
        "latitude": 35.0,
        "longitude": 137.0,
        "place_id": None,
        "image_url": None,
    }


@pytest.fixture
def sample_event_response():
    """テスト用のイベントレスポンスデータ"""
    return {
        "id": 1,
        "ssid": "test_event_001",
        "title": "桶狭間の戦い",
        "start_date": "1560-05-19",
        "end_date": "1560-05-19",
        "description": "織田信長が今川義元を破った戦い",
        "location_name": "桶狭間",
        "latitude": 35.0,
        "longitude": 137.0,
        "place_id": None,
        "image_url": None,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }


@pytest.fixture
def sample_tag_data():
    """テスト用のタグデータ"""
    return {
        "ssid": "test_tag_001",
        "name": "戦国時代",
        "description": "日本の戦国時代に関するタグ",
    }


@pytest.fixture
def sample_tag_response():
    """テスト用のタグレスポンスデータ"""
    return {
        "id": 1,
        "ssid": "test_tag_001",
        "name": "戦国時代",
        "description": "日本の戦国時代に関するタグ",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }


# モックアプリケーション用のフィクスチャ
@pytest.fixture
def mock_app():
    """モックサービスを使用するアプリケーション"""
    from fastapi import FastAPI

    from app.routers import events, persons, tags

    mock_app = FastAPI()

    # ルーターを追加
    mock_app.include_router(persons.router)
    mock_app.include_router(events.router)
    mock_app.include_router(tags.router)

    return mock_app


@pytest.fixture
def mock_client(mock_app):
    """モックアプリケーション用のテストクライアント"""
    return TestClient(mock_app)
