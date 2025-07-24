"""
イベントサービスのテスト

イベントサービスのビジネスロジックをテストします。
"""

from datetime import date

import pytest

from app import schemas
from app.services import EventService


@pytest.mark.service
class TestEventService:
    """イベントサービスのテスト"""

    def test_create_event_success(self, event_service: EventService, db_session):
        """イベント作成の成功テスト"""
        event_data = schemas.EventCreate(
            ssid="test_event_001",
            title="桶狭間の戦い",
            start_date=date(1560, 6, 12),
        )

        event = event_service.create_event(db_session, event_data)

        assert event.id is not None
        assert event.ssid == "test_event_001"
        assert event.title == "桶狭間の戦い"
        assert event.start_date == date(1560, 6, 12)

    def test_create_event_duplicate_ssid(self, event_service: EventService, db_session):
        """重複SSIDでのイベント作成失敗テスト"""
        event_data = schemas.EventCreate(
            ssid="test_event_duplicate",
            title="テストイベント",
            start_date=date(1560, 6, 12),
        )

        # 最初の作成は成功
        event_service.create_event(db_session, event_data)

        # 2回目の作成は失敗
        with pytest.raises(
            ValueError,
            match="SSID 'test_event_duplicate' is already registered",
        ):
            event_service.create_event(db_session, event_data)

    def test_validate_event_data_success(self, event_service: EventService):
        """イベントデータバリデーション成功テスト"""
        event_data = schemas.EventCreate(
            ssid="test_event_valid",
            title="有効なイベント",
            start_date=date(1560, 6, 12),
        )

        # バリデーションが成功することを確認
        event_service.validate_event_data(event_data)

    def test_validate_event_data_missing_title(self, event_service: EventService):
        """タイトル不足でのバリデーション失敗テスト"""
        event_data = schemas.EventCreate(
            ssid="test_event_no_title",
            title="",  # 空のタイトル
            start_date=date(1560, 6, 12),
        )

        with pytest.raises(ValueError, match="Title is required"):
            event_service.validate_event_data(event_data)

    def test_validate_event_data_missing_ssid(self, event_service: EventService):
        """SSID不足でのバリデーション失敗テスト"""
        event_data = schemas.EventCreate(
            ssid="",  # 空のSSID
            title="テストイベント",
            start_date=date(1560, 6, 12),
        )

        with pytest.raises(ValueError, match="SSID is required"):
            event_service.validate_event_data(event_data)

    def test_validate_event_data_invalid_date_range(self, event_service: EventService):
        """無効な日付範囲でのバリデーション失敗テスト"""
        event_data = schemas.EventCreate(
            ssid="test_event_invalid_dates",
            title="無効な日付のイベント",
            start_date=date(1560, 6, 13),  # 開始日が終了日より後
            end_date=date(1560, 6, 12),
        )

        with pytest.raises(ValueError, match="Start date cannot be after end date"):
            event_service.validate_event_data(event_data)

    def test_get_event_success(self, event_service: EventService, db_session):
        """イベント取得の成功テスト"""
        # イベントを作成
        event_data = schemas.EventCreate(
            ssid="test_event_get",
            title="取得テストイベント",
            start_date=date(1560, 6, 12),
        )
        created_event = event_service.create_event(db_session, event_data)

        # イベントを取得
        retrieved_event = event_service.get_event(db_session, created_event.id)

        assert retrieved_event is not None
        assert retrieved_event.ssid == "test_event_get"
        assert retrieved_event.title == "取得テストイベント"

    def test_get_event_not_found(self, event_service: EventService, db_session):
        """存在しないイベントの取得テスト"""
        event = event_service.get_event(db_session, 999)
        assert event is None

    def test_get_event_by_ssid_success(self, event_service: EventService, db_session):
        """SSIDでのイベント取得成功テスト"""
        # イベントを作成
        event_data = schemas.EventCreate(
            ssid="test_event_ssid",
            title="SSID取得テスト",
            start_date=date(1560, 6, 12),
        )
        event_service.create_event(db_session, event_data)

        # SSIDで取得
        retrieved_event = event_service.get_event_by_ssid(db_session, "test_event_ssid")

        assert retrieved_event is not None
        assert retrieved_event.ssid == "test_event_ssid"

    def test_get_event_by_ssid_not_found(self, event_service: EventService, db_session):
        """存在しないSSIDでのイベント取得テスト"""
        event = event_service.get_event_by_ssid(db_session, "non_existent_ssid")
        assert event is None

    def test_update_event_success(self, event_service: EventService, db_session):
        """イベント更新の成功テスト"""
        # イベントを作成
        event_data = schemas.EventCreate(
            ssid="test_event_update",
            title="更新前のタイトル",
            start_date=date(1560, 6, 12),
        )
        created_event = event_service.create_event(db_session, event_data)

        # イベントを更新
        update_data = schemas.EventUpdate(
            title="更新後のタイトル",
            description="更新された説明",
        )
        updated_event = event_service.update_event(db_session, created_event.id, update_data)

        assert updated_event is not None
        assert updated_event.title == "更新後のタイトル"
        assert updated_event.description == "更新された説明"
        assert updated_event.ssid == "test_event_update"  # 変更されていない

    def test_update_event_not_found(self, event_service: EventService, db_session):
        """存在しないイベントの更新テスト"""
        update_data = schemas.EventUpdate(title="更新テスト")
        updated_event = event_service.update_event(db_session, 999, update_data)
        assert updated_event is None

    def test_delete_event_success(self, event_service: EventService, db_session):
        """イベント削除の成功テスト"""
        # イベントを作成
        event_data = schemas.EventCreate(
            ssid="test_event_delete",
            title="削除テストイベント",
            start_date=date(1560, 6, 12),
        )
        created_event = event_service.create_event(db_session, event_data)

        # イベントを削除
        success = event_service.delete_event(db_session, created_event.id)
        assert success is True

        # 削除確認
        deleted_event = event_service.get_event(db_session, created_event.id)
        assert deleted_event is None

    def test_delete_event_not_found(self, event_service: EventService, db_session):
        """存在しないイベントの削除テスト"""
        success = event_service.delete_event(db_session, 999)
        assert success is False
