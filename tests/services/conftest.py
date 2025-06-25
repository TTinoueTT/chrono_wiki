"""
サービス層テスト用のフィクスチャ

サービス層のテストに必要な共通フィクスチャを定義します。
"""

import pytest

from app.services import EventService, PersonService, TagService

# CRUDテストのフィクスチャをインポート（フィクスチャを利用可能にするため）
from tests.crud.conftest import db_session  # noqa: F401


@pytest.fixture
def event_service():
    """イベントサービスのインスタンス"""
    return EventService()


@pytest.fixture
def person_service():
    """人物サービスのインスタンス"""
    return PersonService()


@pytest.fixture
def tag_service():
    """タグサービスのインスタンス"""
    return TagService()
