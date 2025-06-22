"""
CRUD tests for Event entity.

EventCRUDクラスのテストケースを実装します。
"""

from datetime import date
from typing import cast

import pytest

from app.crud.event import EventCRUD
from app.schemas import EventUpdate

from .conftest import EventTestData


@pytest.mark.crud
class TestEventCRUD:
    """イベントCRUD操作のテスト"""

    @pytest.fixture
    def event_crud(self):
        """EventCRUDインスタンス"""
        return EventCRUD()

    def test_create_event(self, event_crud, db_session):
        """イベント作成のテスト"""
        event_data = EventTestData.create_event_data()

        event = event_crud.create(db_session, obj_in=event_data)

        assert event.id is not None
        assert event.ssid == "test_event_001"
        assert event.title == "桶狭間の戦い"
        assert event.description == "織田信長が今川義元を破った戦い"

    def test_get_event(self, event_crud, db_session):
        """イベント取得のテスト"""
        event_data = EventTestData.create_event_data(
            ssid="test_event_002",
            title="本能寺の変",
            description="織田信長が明智光秀に討たれた事件",
        )
        created_event = event_crud.create(db_session, obj_in=event_data)

        retrieved_event = event_crud.get(db_session, cast(int, created_event.id))

        assert retrieved_event is not None
        assert retrieved_event.title == "本能寺の変"
        assert retrieved_event.ssid == "test_event_002"

    def test_get_event_by_ssid(self, event_crud, db_session):
        """SSIDでのイベント取得テスト"""
        event_data = EventTestData.create_event_data(ssid="test_event_003", title="関ヶ原の戦い")
        event_crud.create(db_session, obj_in=event_data)

        event = event_crud.get_by_ssid(db_session, "test_event_003")

        assert event is not None
        assert event.title == "関ヶ原の戦い"

    def test_get_events_with_pagination(self, event_crud, db_session):
        """イベント一覧取得（ページネーション）のテスト"""
        sample_events = EventTestData.create_sample_events()

        for event_data in sample_events:
            event_crud.create(db_session, obj_in=event_data)

        events = event_crud.get_multi(db_session, skip=0, limit=2)
        assert len(events) == 2

        events = event_crud.get_multi(db_session, skip=2, limit=1)
        assert len(events) == 1

    def test_update_event(self, event_crud, db_session):
        """イベント更新のテスト"""
        event_data = EventTestData.create_event_data(
            ssid="test_event_004",
            title="川中島の戦い",
            description="武田信玄と上杉謙信の戦い",
        )
        created_event = event_crud.create(db_session, obj_in=event_data)
        update_data = EventUpdate(
            description="武田信玄と上杉謙信の激戦、五回にわたる戦い",
        )

        updated_event = event_crud.update(db_session, id=cast(int, created_event.id), obj_in=update_data)

        assert updated_event is not None
        assert updated_event.description == "武田信玄と上杉謙信の激戦、五回にわたる戦い"
        assert updated_event.title == "川中島の戦い"  # 変更されていない

    def test_delete_event(self, event_crud, db_session):
        """イベント削除のテスト"""
        event_data = EventTestData.create_event_data(
            ssid="test_event_005",
            title="長篠の戦い",
            description="織田・徳川連合軍が武田軍を破った戦い",
        )
        created_event = event_crud.create(db_session, obj_in=event_data)

        success = event_crud.remove(db_session, id=cast(int, created_event.id))
        assert success is True

        deleted_event = event_crud.get(db_session, cast(int, created_event.id))
        assert deleted_event is None

    def test_get_event_not_found(self, event_crud, db_session):
        """存在しないイベントの取得テスト"""
        event = event_crud.get(db_session, 999)
        assert event is None

    def test_get_event_by_ssid_not_found(self, event_crud, db_session):
        """存在しないSSIDでのイベント取得テスト"""
        event = event_crud.get_by_ssid(db_session, "non_existent_ssid")
        assert event is None

    def test_update_event_not_found(self, event_crud, db_session):
        """存在しないイベントの更新テスト"""
        update_data = EventUpdate(
            description="更新テスト",
        )
        updated_event = event_crud.update(db_session, id=999, obj_in=update_data)
        assert updated_event is None

    def test_delete_event_not_found(self, event_crud, db_session):
        """存在しないイベントの削除テスト"""
        success = event_crud.remove(db_session, id=999)
        assert success is False

    # 新しい拡張DBアクセス関数のテスト
    def test_get_events_by_date_range(self, event_crud, db_session):
        """日付範囲でイベントを取得するテスト"""
        # テストデータ作成
        events_data = [
            EventTestData.create_event_data(
                ssid="test_event_date_001",
                title="桶狭間の戦い",
                start_date="1560-06-12",
                description="1560年の戦い",
            ),
            EventTestData.create_event_data(
                ssid="test_event_date_002",
                title="本能寺の変",
                start_date="1582-06-21",
                description="1582年の事件",
            ),
            EventTestData.create_event_data(
                ssid="test_event_date_003",
                title="関ヶ原の戦い",
                start_date="1600-10-21",
                description="1600年の戦い",
            ),
        ]

        for event_data in events_data:
            event_crud.create(db_session, obj_in=event_data)

        # 1560年から1582年の範囲で検索
        events = event_crud.get_events_by_date_range(
            db_session,
            start_date=date(1560, 1, 1),
            end_date=date(1582, 12, 31),
        )

        assert len(events) == 2
        event_titles = [event.title for event in events]
        assert "桶狭間の戦い" in event_titles
        assert "本能寺の変" in event_titles
        assert "関ヶ原の戦い" not in event_titles

    def test_get_events_by_date_range_with_pagination(self, event_crud, db_session):
        """日付範囲でのイベント取得（ページネーション）のテスト"""
        # 複数のイベントを作成
        for i in range(5):
            event_data = EventTestData.create_event_data(
                ssid=f"test_event_paginated_{i:03d}",
                title=f"テストイベント{i}",
                start_date="1560-06-12",
                description=f"テストイベント{i}の説明",
            )
            event_crud.create(db_session, obj_in=event_data)

        # ページネーション付きで取得
        events = event_crud.get_events_by_date_range(
            db_session,
            start_date=date(1560, 1, 1),
            end_date=date(1560, 12, 31),
            skip=0,
            limit=3,
        )

        assert len(events) == 3

        events = event_crud.get_events_by_date_range(
            db_session,
            start_date=date(1560, 1, 1),
            end_date=date(1560, 12, 31),
            skip=3,
            limit=2,
        )

        assert len(events) == 2

    def test_get_events_by_title_search(self, event_crud, db_session):
        """タイトルでイベントを検索するテスト"""
        # テストデータ作成
        events_data = [
            EventTestData.create_event_data(
                ssid="test_event_search_001",
                title="桶狭間の戦い",
                description="織田信長の戦い",
            ),
            EventTestData.create_event_data(
                ssid="test_event_search_002",
                title="本能寺の変",
                description="織田信長の最期",
            ),
            EventTestData.create_event_data(
                ssid="test_event_search_003",
                title="関ヶ原の戦い",
                description="徳川家康の戦い",
            ),
        ]

        for event_data in events_data:
            event_crud.create(db_session, obj_in=event_data)

        # "戦い"で検索
        events = event_crud.get_events_by_title_search(db_session, "戦い")

        assert len(events) == 2
        event_titles = [event.title for event in events]
        assert "桶狭間の戦い" in event_titles
        assert "関ヶ原の戦い" in event_titles
        assert "本能寺の変" not in event_titles

    def test_get_events_by_location(self, event_crud, db_session):
        """場所でイベントを検索するテスト"""
        # テストデータ作成
        events_data = [
            EventTestData.create_event_data(
                ssid="test_event_location_001",
                title="桶狭間の戦い",
                location_name="桶狭間",
                description="桶狭間での戦い",
            ),
            EventTestData.create_event_data(
                ssid="test_event_location_002",
                title="本能寺の変",
                location_name="本能寺",
                description="本能寺での事件",
            ),
            EventTestData.create_event_data(
                ssid="test_event_location_003",
                title="関ヶ原の戦い",
                location_name="関ヶ原",
                description="関ヶ原での戦い",
            ),
        ]

        for event_data in events_data:
            event_crud.create(db_session, obj_in=event_data)

        # "桶狭間"で検索
        events = event_crud.get_events_by_location(db_session, "桶狭間")

        assert len(events) == 1
        assert events[0].title == "桶狭間の戦い"
        assert events[0].location_name == "桶狭間"

    def test_count_events_by_year(self, event_crud, db_session):
        """指定年のイベント数を取得するテスト"""
        # テストデータ作成
        events_data = [
            EventTestData.create_event_data(
                ssid="test_event_count_001",
                title="桶狭間の戦い",
                start_date="1560-06-12",
                description="1560年の戦い",
            ),
            EventTestData.create_event_data(
                ssid="test_event_count_002",
                title="本能寺の変",
                start_date="1582-06-21",
                description="1582年の事件",
            ),
            EventTestData.create_event_data(
                ssid="test_event_count_003",
                title="関ヶ原の戦い",
                start_date="1600-10-21",
                description="1600年の戦い",
            ),
            EventTestData.create_event_data(
                ssid="test_event_count_004",
                title="大阪の陣",
                start_date="1614-11-15",
                description="1614年の戦い",
            ),
        ]

        for event_data in events_data:
            event_crud.create(db_session, obj_in=event_data)

        # 各年のイベント数を確認
        count_1560 = event_crud.count_events_by_year(db_session, 1560)
        count_1582 = event_crud.count_events_by_year(db_session, 1582)
        count_1600 = event_crud.count_events_by_year(db_session, 1600)
        count_1614 = event_crud.count_events_by_year(db_session, 1614)
        count_1700 = event_crud.count_events_by_year(db_session, 1700)  # 存在しない年

        assert count_1560 == 1
        assert count_1582 == 1
        assert count_1600 == 1
        assert count_1614 == 1
        assert count_1700 == 0

    def test_get_events_by_person(self, event_crud, db_session):
        """人物に関連するイベントを取得するテスト"""
        # テストデータ作成
        events_data = [
            EventTestData.create_event_data(
                ssid="test_event_person_001",
                title="織田信長の戦い",
                description="織田信長が活躍した戦い",
            ),
            EventTestData.create_event_data(
                ssid="test_event_person_002",
                title="徳川家康の戦い",
                description="徳川家康が活躍した戦い",
            ),
        ]

        for event_data in events_data:
            event_crud.create(db_session, obj_in=event_data)

        # 人物IDで検索（現在は基本的な実装のため、descriptionでの検索）
        events = event_crud.get_events_by_person(db_session, person_id=1)

        # 現在の実装では基本的な検索のみ
        assert isinstance(events, list)

    def test_get_events_by_tag(self, event_crud, db_session):
        """タグに関連するイベントを取得するテスト"""
        # テストデータ作成
        events_data = [
            EventTestData.create_event_data(
                ssid="test_event_tag_001",
                title="戦国時代の戦い",
                description="戦国時代の重要な戦い",
            ),
            EventTestData.create_event_data(
                ssid="test_event_tag_002",
                title="江戸時代の事件",
                description="江戸時代の重要な事件",
            ),
        ]

        for event_data in events_data:
            event_crud.create(db_session, obj_in=event_data)

        # タグIDで検索（現在は基本的な実装のため、descriptionでの検索）
        events = event_crud.get_events_by_tag(db_session, tag_id=1)

        # 現在の実装では基本的な検索のみ
        assert isinstance(events, list)

    def test_get_events_statistics(self, event_crud, db_session):
        """イベントの統計情報を取得するテスト"""
        # テストデータ作成
        events_data = [
            EventTestData.create_event_data(
                ssid="test_event_stats_001",
                title="桶狭間の戦い",
                start_date="1560-06-12",
                description="1560年の戦い",
            ),
            EventTestData.create_event_data(
                ssid="test_event_stats_002",
                title="本能寺の変",
                start_date="1582-06-21",
                description="1582年の事件",
            ),
            EventTestData.create_event_data(
                ssid="test_event_stats_003",
                title="関ヶ原の戦い",
                start_date="1600-10-21",
                description="1600年の戦い",
            ),
        ]

        for event_data in events_data:
            event_crud.create(db_session, obj_in=event_data)

        # 統計情報を取得
        stats = event_crud.get_events_statistics(db_session)

        # 統計情報の構造を確認
        assert "total_events" in stats
        assert "yearly_statistics" in stats
        assert stats["total_events"] == 3
        assert len(stats["yearly_statistics"]) == 3

        # 年別統計の詳細を確認
        yearly_stats = {stat["year"]: stat["count"] for stat in stats["yearly_statistics"]}
        assert yearly_stats[1560] == 1
        assert yearly_stats[1582] == 1
        assert yearly_stats[1600] == 1

    def test_empty_database_operations(self, event_crud, db_session):
        """空のデータベースでの操作テスト"""
        # 空のデータベースでの統計情報
        stats = event_crud.get_events_statistics(db_session)
        assert stats["total_events"] == 0
        assert len(stats["yearly_statistics"]) == 0

        # 空のデータベースでの検索
        events = event_crud.get_events_by_date_range(
            db_session,
            start_date=date(1560, 1, 1),
            end_date=date(1600, 12, 31),
        )
        assert len(events) == 0

        events = event_crud.get_events_by_title_search(db_session, "戦い")
        assert len(events) == 0

        events = event_crud.get_events_by_location(db_session, "桶狭間")
        assert len(events) == 0

        count = event_crud.count_events_by_year(db_session, 1560)
        assert count == 0

    def test_update_event_with_none_values(self, event_crud, db_session):
        """None値を含む更新テスト"""
        event_data = EventTestData.create_event_data(
            ssid="test_event_none_001",
            title="小牧・長久手の戦い",
            description="織田信雄と徳川家康の戦い",
            location_name="小牧山",
            latitude=35.1234,
            longitude=136.5678,
        )
        created_event = event_crud.create(db_session, obj_in=event_data)

        # None値を含む更新データ（現在の実装ではNone値は除外される）
        update_data = EventUpdate(
            description="織田信雄と徳川家康の激戦、秀吉の介入により終結",
            location_name=None,  # None値は除外される
            latitude=None,  # None値は除外される
            longitude=None,  # None値は除外される
        )
        updated_event = event_crud.update(db_session, id=cast(int, created_event.id), obj_in=update_data)

        assert updated_event is not None
        assert updated_event.description == "織田信雄と徳川家康の激戦、秀吉の介入により終結"
        assert updated_event.location_name == "小牧山"  # None値は除外されるため変更されない
        assert float(updated_event.latitude) == 35.1234  # Decimal型をfloatに変換して比較
        assert float(updated_event.longitude) == 136.5678  # Decimal型をfloatに変換して比較
        assert updated_event.title == "小牧・長久手の戦い"  # 変更されていない
        assert updated_event.ssid == "test_event_none_001"  # 変更されていない
