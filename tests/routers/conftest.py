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

from app.core import setup_test_logging
from app.database import get_db
from app.dependencies.api_key_auth import verify_token
from app.main import app
from app.models.base import Base
from app.models.user import User
from app.services import EventService, PersonService, TagService


# テスト用の環境変数を設定
@pytest.fixture(autouse=True)
def setup_test_env():
    """テスト用の環境変数を設定"""
    # テスト用ログ設定
    setup_test_logging()

    # PostgreSQL 17を使用したテスト環境
    test_db_url = os.getenv("TEST_DATABASE_URL")
    if not test_db_url:
        raise ValueError("TEST_DATABASE_URL environment variable is required for tests")

    # os.environ["DATABASE_URL"] = test_db_url
    # os.environ["TEST_DATABASE_URL"] = test_db_url

    # テスト用DBの初期化を確実に行う
    from sqlalchemy import create_engine

    from app.models.base import Base

    engine = create_engine(test_db_url)
    Base.metadata.create_all(bind=engine)
    engine.dispose()

    yield

    # テスト後のクリーンアップ
    engine = create_engine(test_db_url)
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


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


def mock_get_current_user():
    """テスト用の現在のユーザー取得関数"""
    from datetime import datetime

    from app.models.user import User

    return User(
        id="test-user-id",
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        role="user",
        last_login=None,
        failed_login_attempts="0",
        locked_until=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def mock_get_current_active_user():
    """テスト用の現在のアクティブユーザー取得関数"""
    return mock_get_current_user()


def mock_require_auth():
    """テスト用の認証要求関数"""
    return mock_get_current_user()


def mock_require_moderator():
    """テスト用のモデレーター権限要求関数"""
    user = mock_get_current_user()
    user.role = "moderator"
    return user


def mock_require_admin():
    """テスト用の管理者権限要求関数"""
    user = mock_get_current_user()
    user.role = "admin"
    return user


@pytest.fixture
def client(test_db_session):
    """FastAPIテストクライアント（実際のDB使用・実際のAPIキー認証）"""

    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    # データベース依存性をオーバーライド
    app.dependency_overrides[get_db] = override_get_db

    # 認証モックをクリアして実際のAPIキー認証を使用
    if verify_token in app.dependency_overrides:
        del app.dependency_overrides[verify_token]

    yield TestClient(app)

    # クリーンアップ
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(test_db_session):
    """認証機能付きFastAPIテストクライアント（実際のDB使用・実際のAPIキー認証）"""

    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    # データベース依存性をオーバーライド
    app.dependency_overrides[get_db] = override_get_db

    # 認証モックをクリアして実際のAPIキー認証を使用
    if verify_token in app.dependency_overrides:
        del app.dependency_overrides[verify_token]

    # テスト前にデータベースをクリーンアップ
    test_db_session.query(User).delete()
    test_db_session.commit()

    yield TestClient(app)

    # テスト後にデータベースをクリーンアップ
    test_db_session.query(User).delete()
    test_db_session.commit()

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


# ユーザーテスト用のフィクスチャ
@pytest.fixture
def sample_user_data():
    """テスト用のユーザーデータ"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User",
        "role": "user",
        "is_active": True,
    }


@pytest.fixture
def sample_user_response():
    """テスト用のユーザーレスポンスデータ"""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "avatar_url": None,
        "bio": None,
        "is_active": True,
        "is_superuser": False,
        "role": "user",
        "last_login": None,
        "failed_login_attempts": "0",
        "locked_until": None,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }


@pytest.fixture
def admin_user_data():
    """テスト用の管理者ユーザーデータ"""
    return {
        "email": "admin@example.com",
        "username": "admin",
        "password": "adminpassword123",
        "full_name": "Admin User",
        "role": "admin",
        "is_active": True,
    }


@pytest.fixture
def moderator_user_data():
    """テスト用のモデレーターユーザーデータ"""
    return {
        "email": "moderator@example.com",
        "username": "moderator",
        "password": "moderatorpassword123",
        "full_name": "Moderator User",
        "role": "moderator",
        "is_active": True,
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


@pytest.fixture
def api_key_headers():
    """APIキー認証用のヘッダー"""
    api_key = os.getenv("API_KEY", "")
    if not api_key:
        raise ValueError("API_KEY environment variable is required")
    return {"X-API-Key": api_key}


@pytest.fixture
def jwt_headers():
    """JWT認証用のヘッダー（テスト用トークン）"""
    return {"Authorization": "Bearer test_jwt_token"}


@pytest.fixture
def admin_headers():
    """管理者権限用のヘッダー"""
    return {"Authorization": "Bearer admin_jwt_token"}


@pytest.fixture
def moderator_headers():
    """モデレーター権限用のヘッダー"""
    return {"Authorization": "Bearer moderator_jwt_token"}


@pytest.fixture
def user_headers():
    """一般ユーザー権限用のヘッダー"""
    return {"Authorization": "Bearer user_jwt_token"}


def mock_get_current_admin():
    """テスト用の管理者ユーザー取得関数"""
    from unittest.mock import Mock

    from app.enums import UserRole
    from app.models.user import User

    user = Mock(spec=User)
    user.id = "admin_user_id"
    user.username = "admin_user"
    user.email = "admin@example.com"
    user.role = UserRole.ADMIN.value
    user.is_active = True
    user.is_verified = True

    return user


def mock_get_current_moderator():
    """テスト用のモデレーター取得関数"""
    from unittest.mock import Mock

    from app.enums import UserRole
    from app.models.user import User

    user = Mock(spec=User)
    user.id = "moderator_user_id"
    user.username = "moderator_user"
    user.email = "moderator@example.com"
    user.role = UserRole.MODERATOR.value
    user.is_active = True
    user.is_verified = True

    return user
