"""
CRUD tests for Tag entity.

TagCRUDクラスのテストケースを実装します。
"""

from typing import cast

import pytest

from app.crud.tag import TagCRUD
from app.schemas import TagUpdate

from .conftest import TagTestData


@pytest.mark.crud
class TestTagCRUD:
    """タグCRUD操作のテスト"""

    @pytest.fixture
    def tag_crud(self):
        """TagCRUDインスタンス"""
        return TagCRUD()

    def test_create_tag(self, tag_crud, db_session):
        """タグ作成のテスト"""
        tag_data = TagTestData.create_tag_data()

        tag = tag_crud.create(db_session, obj_in=tag_data)

        assert tag.id is not None
        assert tag.ssid == "test_tag_001"
        assert tag.name == "戦国武将"
        assert tag.description == "戦国時代の武将"

    def test_get_tag(self, tag_crud, db_session):
        """タグ取得のテスト"""
        tag_data = TagTestData.create_tag_data(ssid="test_tag_002", name="大名", description="地方の支配者")
        created_tag = tag_crud.create(db_session, obj_in=tag_data)

        retrieved_tag = tag_crud.get(db_session, cast(int, created_tag.id))

        assert retrieved_tag is not None
        assert retrieved_tag.name == "大名"
        assert retrieved_tag.ssid == "test_tag_002"

    def test_get_tag_by_ssid(self, tag_crud, db_session):
        """SSIDでのタグ取得テスト"""
        tag_data = TagTestData.create_tag_data(ssid="test_tag_003", name="軍師")
        tag_crud.create(db_session, obj_in=tag_data)

        tag = tag_crud.get_by_ssid(db_session, "test_tag_003")

        assert tag is not None
        assert tag.name == "軍師"

    def test_get_tags_with_pagination(self, tag_crud, db_session):
        """タグ一覧取得（ページネーション）のテスト"""
        sample_tags = TagTestData.create_sample_tags()

        for tag_data in sample_tags:
            tag_crud.create(db_session, obj_in=tag_data)

        tags = tag_crud.get_multi(db_session, skip=0, limit=2)
        assert len(tags) == 2

        tags = tag_crud.get_multi(db_session, skip=2, limit=1)
        assert len(tags) == 1

    def test_update_tag(self, tag_crud, db_session):
        """タグ更新のテスト"""
        tag_data = TagTestData.create_tag_data(ssid="test_tag_004", name="武将", description="戦の指揮を取る者")
        created_tag = tag_crud.create(db_session, obj_in=tag_data)

        update_data = TagUpdate(description="戦の指揮を取る者、勇猛な戦士")
        updated_tag = tag_crud.update(db_session, id=cast(int, created_tag.id), obj_in=update_data)

        assert updated_tag is not None
        assert updated_tag.description == "戦の指揮を取る者、勇猛な戦士"
        assert updated_tag.name == "武将"  # 変更されていない

    def test_delete_tag(self, tag_crud, db_session):
        """タグ削除のテスト"""
        tag_data = TagTestData.create_tag_data(ssid="test_tag_005", name="忍者", description="諜報活動を行う者")
        created_tag = tag_crud.create(db_session, obj_in=tag_data)

        success = tag_crud.remove(db_session, id=cast(int, created_tag.id))
        assert success is True

        deleted_tag = tag_crud.get(db_session, cast(int, created_tag.id))
        assert deleted_tag is None

    def test_get_tag_not_found(self, tag_crud, db_session):
        """存在しないタグの取得テスト"""
        tag = tag_crud.get(db_session, 999)
        assert tag is None

    def test_get_tag_by_ssid_not_found(self, tag_crud, db_session):
        """存在しないSSIDでのタグ取得テスト"""
        tag = tag_crud.get_by_ssid(db_session, "non_existent_ssid")
        assert tag is None

    def test_update_tag_not_found(self, tag_crud, db_session):
        """存在しないタグの更新テスト"""
        update_data = TagUpdate(description="更新テスト")
        updated_tag = tag_crud.update(db_session, id=999, obj_in=update_data)
        assert updated_tag is None

    def test_delete_tag_not_found(self, tag_crud, db_session):
        """存在しないタグの削除テスト"""
        success = tag_crud.remove(db_session, id=999)
        assert success is False

    def test_update_tag_partial(self, tag_crud, db_session):
        """タグの部分更新テスト"""
        tag_data = TagTestData.create_tag_data(
            ssid="test_tag_006",
            name="茶人",
            description="茶道を嗜む者",
        )
        created_tag = tag_crud.create(db_session, obj_in=tag_data)

        # 部分更新（descriptionのみ）
        update_data = TagUpdate(description="茶道の達人、千利休のような人物")
        updated_tag = tag_crud.update(db_session, id=cast(int, created_tag.id), obj_in=update_data)

        assert updated_tag is not None
        assert updated_tag.description == "茶道の達人、千利休のような人物"
        assert updated_tag.name == "茶人"  # 変更されていない
        assert updated_tag.ssid == "test_tag_006"  # 変更されていない

    def test_update_tag_with_none_values(self, tag_crud, db_session):
        """None値を含む更新テスト"""
        tag_data = TagTestData.create_tag_data(
            ssid="test_tag_007",
            name="商人",
            description="商業を営む者",
        )
        created_tag = tag_crud.create(db_session, obj_in=tag_data)

        # None値を含む更新データ（現在の実装ではNone値は除外される）
        update_data = TagUpdate(
            name="豪商",
            description=None,  # None値は除外される
        )
        updated_tag = tag_crud.update(db_session, id=cast(int, created_tag.id), obj_in=update_data)

        assert updated_tag is not None
        assert updated_tag.name == "豪商"
        assert updated_tag.description == "商業を営む者"  # None値は除外されるため変更されない
        assert updated_tag.ssid == "test_tag_007"  # 変更されていない

    def test_create_multiple_tags(self, tag_crud, db_session):
        """複数タグの作成テスト"""
        tag_data_list = [
            TagTestData.create_tag_data(ssid="test_tag_multi_001", name="戦国大名", description="戦国時代の大名"),
            TagTestData.create_tag_data(ssid="test_tag_multi_002", name="武将", description="戦の指揮官"),
            TagTestData.create_tag_data(ssid="test_tag_multi_003", name="軍師", description="戦略を練る者"),
        ]

        created_tags = []
        for tag_data in tag_data_list:
            tag = tag_crud.create(db_session, obj_in=tag_data)
            created_tags.append(tag)

        assert len(created_tags) == 3
        assert created_tags[0].name == "戦国大名"
        assert created_tags[1].name == "武将"
        assert created_tags[2].name == "軍師"

        # 全件取得で確認
        all_tags = tag_crud.get_multi(db_session, skip=0, limit=100)
        assert len(all_tags) >= 3
