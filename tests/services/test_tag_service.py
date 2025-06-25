# type: ignore

"""
タグサービスのテスト

タグサービスのビジネスロジックをテストします。
"""

import pytest

from app import schemas
from app.services import TagService


@pytest.mark.service
class TestTagService:
    """タグサービスのテスト"""

    def test_create_tag_success(self, tag_service: TagService, db_session):
        """タグ作成の成功テスト"""
        tag_data = schemas.TagCreate(
            ssid="test_tag_001",
            name="戦国武将",
            description="戦国時代の武将",
        )

        tag = tag_service.create_tag(db_session, tag_data)

        assert tag.id is not None
        assert tag.ssid == "test_tag_001"
        assert tag.name == "戦国武将"
        assert tag.description == "戦国時代の武将"

    def test_create_tag_duplicate_ssid(self, tag_service: TagService, db_session):
        """重複SSIDでのタグ作成失敗テスト"""
        tag_data = schemas.TagCreate(
            ssid="test_tag_duplicate",
            name="テストタグ",
            description="テスト用タグ",
        )

        # 最初の作成は成功
        tag_service.create_tag(db_session, tag_data)

        # 2回目の作成は失敗
        with pytest.raises(ValueError, match="SSID 'test_tag_duplicate' is already registered"):
            tag_service.create_tag(db_session, tag_data)

    def test_validate_tag_data_success(self, tag_service: TagService):
        """タグデータバリデーション成功テスト"""
        tag_data = schemas.TagCreate(
            ssid="test_tag_valid",
            name="有効なタグ",
            description="有効なタグの説明",
        )

        # バリデーションが成功することを確認
        tag_service.validate_tag_data(tag_data)

    def test_validate_tag_data_missing_name(self, tag_service: TagService):
        """タグ名不足でのバリデーション失敗テスト"""
        tag_data = schemas.TagCreate(
            ssid="test_tag_no_name",
            name="",  # 空のタグ名
            description="テスト用タグ",
        )

        with pytest.raises(ValueError, match="Tag name is required"):
            tag_service.validate_tag_data(tag_data)

    def test_validate_tag_data_missing_ssid(self, tag_service: TagService):
        """SSID不足でのバリデーション失敗テスト"""
        tag_data = schemas.TagCreate(
            ssid="",  # 空のSSID
            name="テストタグ",
            description="テスト用タグ",
        )

        with pytest.raises(ValueError, match="SSID is required"):
            tag_service.validate_tag_data(tag_data)

    def test_validate_tag_data_empty_name(self, tag_service: TagService):
        """空のタグ名でのバリデーション失敗テスト"""
        tag_data = schemas.TagCreate(
            ssid="test_tag_empty_name",
            name="   ",  # 空白文字のみ
            description="テスト用タグ",
        )

        with pytest.raises(ValueError, match="Tag name is required"):
            tag_service.validate_tag_data(tag_data)

    def test_get_tag_success(self, tag_service: TagService, db_session):
        """タグ取得の成功テスト"""
        # タグを作成
        tag_data = schemas.TagCreate(
            ssid="test_tag_get",
            name="取得テストタグ",
            description="取得テスト用タグ",
        )
        created_tag = tag_service.create_tag(db_session, tag_data)

        # タグを取得
        retrieved_tag = tag_service.get_tag(db_session, created_tag.id)

        assert retrieved_tag is not None
        assert retrieved_tag.ssid == "test_tag_get"
        assert retrieved_tag.name == "取得テストタグ"

    def test_get_tag_not_found(self, tag_service: TagService, db_session):
        """存在しないタグの取得テスト"""
        tag = tag_service.get_tag(db_session, 999)
        assert tag is None

    def test_get_tag_by_ssid_success(self, tag_service: TagService, db_session):
        """SSIDでのタグ取得成功テスト"""
        # タグを作成
        tag_data = schemas.TagCreate(
            ssid="test_tag_ssid",
            name="SSID取得テスト",
            description="SSID取得テスト用タグ",
        )
        tag_service.create_tag(db_session, tag_data)

        # SSIDで取得
        retrieved_tag = tag_service.get_tag_by_ssid(db_session, "test_tag_ssid")

        assert retrieved_tag is not None
        assert retrieved_tag.ssid == "test_tag_ssid"

    def test_get_tag_by_ssid_not_found(self, tag_service: TagService, db_session):
        """存在しないSSIDでのタグ取得テスト"""
        tag = tag_service.get_tag_by_ssid(db_session, "non_existent_ssid")
        assert tag is None

    def test_update_tag_success(self, tag_service: TagService, db_session):
        """タグ更新の成功テスト"""
        # タグを作成
        tag_data = schemas.TagCreate(
            ssid="test_tag_update",
            name="更新前のタグ名",
            description="更新前の説明",
        )
        created_tag = tag_service.create_tag(db_session, tag_data)

        # タグを更新
        update_data = schemas.TagUpdate(
            name="更新後のタグ名",
            description="更新された説明",
        )
        updated_tag = tag_service.update_tag(db_session, created_tag.id, update_data)

        assert updated_tag is not None
        assert updated_tag.name == "更新後のタグ名"
        assert updated_tag.description == "更新された説明"
        assert updated_tag.ssid == "test_tag_update"  # 変更されていない

    def test_update_tag_not_found(self, tag_service: TagService, db_session):
        """存在しないタグの更新テスト"""
        update_data = schemas.TagUpdate(name="更新テスト")
        updated_tag = tag_service.update_tag(db_session, 999, update_data)
        assert updated_tag is None

    def test_delete_tag_success(self, tag_service: TagService, db_session):
        """タグ削除の成功テスト"""
        # タグを作成
        tag_data = schemas.TagCreate(
            ssid="test_tag_delete",
            name="削除テストタグ",
            description="削除テスト用タグ",
        )
        created_tag = tag_service.create_tag(db_session, tag_data)

        # タグを削除
        success = tag_service.delete_tag(db_session, created_tag.id)
        assert success is True

        # 削除確認
        deleted_tag = tag_service.get_tag(db_session, created_tag.id)
        assert deleted_tag is None

    def test_delete_tag_not_found(self, tag_service: TagService, db_session):
        """存在しないタグの削除テスト"""
        success = tag_service.delete_tag(db_session, 999)
        assert success is False

    def test_get_tags_with_pagination(self, tag_service: TagService, db_session):
        """タグ一覧取得（ページネーション）のテスト"""
        # 複数のタグを作成
        tag_data1 = schemas.TagCreate(
            ssid="test_tag_001",
            name="タグ1",
            description="1番目のタグ",
        )
        tag_data2 = schemas.TagCreate(
            ssid="test_tag_002",
            name="タグ2",
            description="2番目のタグ",
        )
        tag_data3 = schemas.TagCreate(
            ssid="test_tag_003",
            name="タグ3",
            description="3番目のタグ",
        )

        tag_service.create_tag(db_session, tag_data1)
        tag_service.create_tag(db_session, tag_data2)
        tag_service.create_tag(db_session, tag_data3)

        # ページネーションテスト
        tags = tag_service.get_tags(db_session, skip=0, limit=2)
        assert len(tags) == 2

        tags = tag_service.get_tags(db_session, skip=2, limit=1)
        assert len(tags) == 1
