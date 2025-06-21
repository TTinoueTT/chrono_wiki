"""
CRUD tests for Event entity.
"""

from typing import cast

import pytest

from app.crud import event as crud
from app.schemas import EventUpdate

from .conftest import EventTestData


@pytest.mark.crud
class TestEventCRUD:
    """イベントCRUD操作のテスト"""

    def test_create_event(self, db_session):
        """イベント作成のテスト"""
        event_data = EventTestData.create_event_data()

        event = crud.create_event(db_session, event_data)

        assert event.id is not None  # type: ignore
        assert event.ssid == "test_event_001"  # type: ignore
        assert event.title == "桶狭間の戦い"  # type: ignore
        assert event.description == "織田信長が今川義元を破った戦い"  # type: ignore

    def test_get_event(self, db_session):
        """イベント取得のテスト"""
        event_data = EventTestData.create_event_data(
            ssid="test_event_002",
            title="本能寺の変",
            description="織田信長が明智光秀に討たれた事件",
        )
        created_event = crud.create_event(db_session, event_data)

        retrieved_event = crud.get_event(
            db_session, cast(int, created_event.id)
        )

        assert retrieved_event is not None
        assert retrieved_event.title == "本能寺の変"  # type: ignore
        assert retrieved_event.ssid == "test_event_002"  # type: ignore

    def test_get_event_by_ssid(self, db_session):
        """SSIDでのイベント取得テスト"""
        event_data = EventTestData.create_event_data(
            ssid="test_event_003", title="関ヶ原の戦い"
        )
        crud.create_event(db_session, event_data)

        event = crud.get_event_by_ssid(db_session, "test_event_003")

        assert event is not None
        assert event.title == "関ヶ原の戦い"  # type: ignore

    def test_get_events_with_pagination(self, db_session):
        """イベント一覧取得（ページネーション）のテスト"""
        sample_events = EventTestData.create_sample_events()

        for event_data in sample_events:
            crud.create_event(db_session, event_data)

        events = crud.get_events(db_session, skip=0, limit=2)
        assert len(events) == 2

        events = crud.get_events(db_session, skip=2, limit=1)
        assert len(events) == 1

    def test_update_event(self, db_session):
        """イベント更新のテスト"""
        event_data = EventTestData.create_event_data(
            ssid="test_event_004",
            title="川中島の戦い",
            description="武田信玄と上杉謙信の戦い",
        )
        created_event = crud.create_event(db_session, event_data)

        update_data = EventUpdate(  # type: ignore
            description="武田信玄と上杉謙信の激戦、五回にわたる戦い"
        )
        updated_event = crud.update_event(
            db_session, cast(int, created_event.id), update_data
        )

        assert updated_event is not None
        assert (
            updated_event.description  # type: ignore
            == "武田信玄と上杉謙信の激戦、五回にわたる戦い"
        )
        assert updated_event.title == "川中島の戦い"  # type: ignore  # 変更されていない

    def test_delete_event(self, db_session):
        """イベント削除のテスト"""
        event_data = EventTestData.create_event_data(
            ssid="test_event_005",
            title="長篠の戦い",
            description="織田・徳川連合軍が武田軍を破った戦い",
        )
        created_event = crud.create_event(db_session, event_data)

        success = crud.delete_event(db_session, cast(int, created_event.id))
        assert success is True

        deleted_event = crud.get_event(db_session, cast(int, created_event.id))
        assert deleted_event is None

    def test_get_event_not_found(self, db_session):
        """存在しないイベントの取得テスト"""
        event = crud.get_event(db_session, 999)
        assert event is None

    def test_get_event_by_ssid_not_found(self, db_session):
        """存在しないSSIDでのイベント取得テスト"""
        event = crud.get_event_by_ssid(db_session, "non_existent_ssid")
        assert event is None

    def test_update_event_not_found(self, db_session):
        """存在しないイベントの更新テスト"""
        update_data = EventUpdate(
            title=None,
            start_data=None,
            end_data=None,
            description="更新テスト",
            location_name=None,
            latitude=None,
            longitude=None,
            place_id=None,
            image_url=None,
        )
        updated_event = crud.update_event(db_session, 999, update_data)
        assert updated_event is None

    def test_delete_event_not_found(self, db_session):
        """存在しないイベントの削除テスト"""
        success = crud.delete_event(db_session, 999)
        assert success is False
