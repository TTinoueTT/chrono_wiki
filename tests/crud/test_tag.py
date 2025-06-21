"""
CRUD tests for Tag entity.
"""

from typing import cast

import pytest

from app.crud import tag as crud
from app.schemas import TagUpdate

from .conftest import TagTestData


@pytest.mark.crud
class TestTagCRUD:
    """タグCRUD操作のテスト"""

    def test_create_tag(self, db_session):
        """タグ作成のテスト"""
        tag_data = TagTestData.create_tag_data()

        tag = crud.create_tag(db_session, tag_data)

        assert tag.id is not None  # type: ignore
        assert tag.ssid == "test_tag_001"  # type: ignore
        assert tag.name == "戦国武将"  # type: ignore
        assert tag.description == "戦国時代の武将"  # type: ignore

    def test_get_tag(self, db_session):
        """タグ取得のテスト"""
        tag_data = TagTestData.create_tag_data(
            ssid="test_tag_002", name="大名", description="地方の支配者"
        )
        created_tag = crud.create_tag(db_session, tag_data)

        retrieved_tag = crud.get_tag(db_session, cast(int, created_tag.id))

        assert retrieved_tag is not None
        assert retrieved_tag.name == "大名"  # type: ignore
        assert retrieved_tag.ssid == "test_tag_002"  # type: ignore

    def test_get_tag_by_ssid(self, db_session):
        """SSIDでのタグ取得テスト"""
        tag_data = TagTestData.create_tag_data(
            ssid="test_tag_003", name="軍師"
        )
        crud.create_tag(db_session, tag_data)

        tag = crud.get_tag_by_ssid(db_session, "test_tag_003")

        assert tag is not None
        assert tag.name == "軍師"  # type: ignore

    def test_get_tags_with_pagination(self, db_session):
        """タグ一覧取得（ページネーション）のテスト"""
        sample_tags = TagTestData.create_sample_tags()

        for tag_data in sample_tags:
            crud.create_tag(db_session, tag_data)

        tags = crud.get_tags(db_session, skip=0, limit=2)
        assert len(tags) == 2

        tags = crud.get_tags(db_session, skip=2, limit=1)
        assert len(tags) == 1

    def test_update_tag(self, db_session):
        """タグ更新のテスト"""
        tag_data = TagTestData.create_tag_data(
            ssid="test_tag_004", name="武将", description="戦の指揮を取る者"
        )
        created_tag = crud.create_tag(db_session, tag_data)

        update_data = TagUpdate(description="戦の指揮を取る者、勇猛な戦士")  # type: ignore
        updated_tag = crud.update_tag(
            db_session, cast(int, created_tag.id), update_data
        )

        assert updated_tag is not None
        assert updated_tag.description == "戦の指揮を取る者、勇猛な戦士"  # type: ignore
        assert updated_tag.name == "武将"  # type: ignore  # 変更されていない

    def test_delete_tag(self, db_session):
        """タグ削除のテスト"""
        tag_data = TagTestData.create_tag_data(
            ssid="test_tag_005", name="忍者", description="諜報活動を行う者"
        )
        created_tag = crud.create_tag(db_session, tag_data)

        success = crud.delete_tag(db_session, cast(int, created_tag.id))
        assert success is True

        deleted_tag = crud.get_tag(db_session, cast(int, created_tag.id))
        assert deleted_tag is None

    def test_get_tag_not_found(self, db_session):
        """存在しないタグの取得テスト"""
        tag = crud.get_tag(db_session, 999)
        assert tag is None

    def test_get_tag_by_ssid_not_found(self, db_session):
        """存在しないSSIDでのタグ取得テスト"""
        tag = crud.get_tag_by_ssid(db_session, "non_existent_ssid")
        assert tag is None

    def test_update_tag_not_found(self, db_session):
        """存在しないタグの更新テスト"""
        update_data = TagUpdate(name=None, description="更新テスト")
        updated_tag = crud.update_tag(db_session, 999, update_data)
        assert updated_tag is None

    def test_delete_tag_not_found(self, db_session):
        """存在しないタグの削除テスト"""
        success = crud.delete_tag(db_session, 999)
        assert success is False
