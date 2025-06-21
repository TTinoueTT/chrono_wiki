"""
CRUD tests for Person entity.
"""

from typing import cast

import pytest

from app.crud import person as crud
from app.schemas import PersonUpdate

from .conftest import PersonTestData


@pytest.mark.crud
class TestPersonCRUD:
    """人物CRUD操作のテスト"""

    def test_create_person(self, db_session):
        """人物作成のテスト"""
        person_data = PersonTestData.create_person_data()

        person = crud.create_person(db_session, person_data)

        assert person.id is not None  # type: ignore
        assert person.ssid == "test_person_001"  # type: ignore
        assert person.full_name == "織田信長"  # type: ignore
        assert person.birth_date.year == 1534  # type: ignore

    def test_get_person(self, db_session):
        """人物取得のテスト"""
        # テストデータ作成
        person_data = PersonTestData.create_person_data(
            ssid="test_person_002", full_name="豊臣秀吉"
        )
        created_person = crud.create_person(db_session, person_data)

        # 取得テスト
        retrieved_person = crud.get_person(
            db_session, cast(int, created_person.id)
        )

        assert retrieved_person is not None
        assert retrieved_person.full_name == "豊臣秀吉"  # type: ignore
        assert retrieved_person.ssid == "test_person_002"  # type: ignore

    def test_get_person_by_ssid(self, db_session):
        """SSIDでの人物取得テスト"""
        person_data = PersonTestData.create_person_data(
            ssid="test_person_003", full_name="徳川家康"
        )
        crud.create_person(db_session, person_data)

        # SSIDで取得
        person = crud.get_person_by_ssid(db_session, "test_person_003")

        assert person is not None
        assert person.full_name == "徳川家康"  # type: ignore

    def test_get_persons_with_pagination(self, db_session):
        """人物一覧取得（ページネーション）のテスト"""
        # 複数のテストデータ作成
        sample_persons = PersonTestData.create_sample_persons()

        for person_data in sample_persons:
            crud.create_person(db_session, person_data)

        # ページネーションテスト
        persons = crud.get_persons(db_session, skip=0, limit=2)
        assert len(persons) == 2

        persons = crud.get_persons(db_session, skip=2, limit=1)
        assert len(persons) == 1

    def test_update_person(self, db_session):
        """人物更新のテスト"""
        person_data = PersonTestData.create_person_data(
            ssid="test_person_004",
            full_name="武田信玄",
            description="甲斐の虎",
        )
        created_person = crud.create_person(db_session, person_data)

        # 更新データ
        update_data = PersonUpdate(description="甲斐の虎、風林火山")  # type: ignore
        updated_person = crud.update_person(
            db_session, cast(int, created_person.id), update_data
        )

        assert updated_person is not None
        assert updated_person.description == "甲斐の虎、風林火山"  # type: ignore
        assert updated_person.full_name == "武田信玄"  # type: ignore  # 変更されていない

    def test_delete_person(self, db_session):
        """人物削除のテスト"""
        person_data = PersonTestData.create_person_data(
            ssid="test_person_005",
            full_name="上杉謙信",
            description="越後の龍",
        )
        created_person = crud.create_person(db_session, person_data)

        # 削除実行
        success = crud.delete_person(db_session, cast(int, created_person.id))
        assert success is True

        # 削除確認
        deleted_person = crud.get_person(
            db_session, cast(int, created_person.id)
        )
        assert deleted_person is None

    def test_get_person_not_found(self, db_session):
        """存在しない人物の取得テスト"""
        person = crud.get_person(db_session, 999)
        assert person is None

    def test_get_person_by_ssid_not_found(self, db_session):
        """存在しないSSIDでの人物取得テスト"""
        person = crud.get_person_by_ssid(db_session, "non_existent_ssid")
        assert person is None

    def test_update_person_not_found(self, db_session):
        """存在しない人物の更新テスト"""
        update_data = PersonUpdate(
            full_name=None,
            display_name=None,
            search_name=None,
            birth_date=None,
            death_date=None,
            born_country=None,
            born_region=None,
            description="更新テスト",
            portrait_url=None,
        )
        updated_person = crud.update_person(db_session, 999, update_data)
        assert updated_person is None

    def test_delete_person_not_found(self, db_session):
        """存在しない人物の削除テスト"""
        success = crud.delete_person(db_session, 999)
        assert success is False
