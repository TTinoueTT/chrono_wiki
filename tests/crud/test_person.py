"""
CRUD tests for Person entity.

PersonCRUDクラスのテストケースを実装します。
"""

from typing import cast

import pytest

from app.crud.person import PersonCRUD
from app.schemas import PersonUpdate

from .conftest import PersonTestData


@pytest.mark.crud
class TestPersonCRUD:
    """人物CRUD操作のテスト"""

    @pytest.fixture
    def person_crud(self):
        """PersonCRUDインスタンス"""
        return PersonCRUD()

    def test_create_person(self, person_crud, db_session):
        """人物作成のテスト"""
        person_data = PersonTestData.create_person_data()

        person = person_crud.create(db_session, obj_in=person_data)

        assert person.id is not None
        assert person.ssid == "test_person_001"
        assert person.full_name == "織田信長"
        assert person.birth_date.year == 1534

    def test_get_person(self, person_crud, db_session):
        """人物取得のテスト"""
        person_data = PersonTestData.create_person_data(ssid="test_person_002", full_name="豊臣秀吉")
        created_person = person_crud.create(db_session, obj_in=person_data)

        retrieved_person = person_crud.get(db_session, cast(int, created_person.id))

        assert retrieved_person is not None
        assert retrieved_person.full_name == "豊臣秀吉"
        assert retrieved_person.ssid == "test_person_002"

    def test_get_person_by_ssid(self, person_crud, db_session):
        """SSIDでの人物取得テスト"""
        person_data = PersonTestData.create_person_data(ssid="test_person_003", full_name="徳川家康")
        person_crud.create(db_session, obj_in=person_data)

        person = person_crud.get_by_ssid(db_session, "test_person_003")

        assert person is not None
        assert person.full_name == "徳川家康"

    def test_get_persons_with_pagination(self, person_crud, db_session):
        """人物一覧取得（ページネーション）のテスト"""
        sample_persons = PersonTestData.create_sample_persons()

        for person_data in sample_persons:
            person_crud.create(db_session, obj_in=person_data)

        persons = person_crud.get_multi(db_session, skip=0, limit=2)
        assert len(persons) == 2

        persons = person_crud.get_multi(db_session, skip=2, limit=1)
        assert len(persons) == 1

    def test_update_person(self, person_crud, db_session):
        """人物更新のテスト"""
        person_data = PersonTestData.create_person_data(
            ssid="test_person_004",
            full_name="武田信玄",
            description="甲斐の虎",
        )
        created_person = person_crud.create(db_session, obj_in=person_data)

        update_data = PersonUpdate(description="甲斐の虎、風林火山")
        updated_person = person_crud.update(db_session, id=cast(int, created_person.id), obj_in=update_data)

        assert updated_person is not None
        assert updated_person.description == "甲斐の虎、風林火山"
        assert updated_person.full_name == "武田信玄"  # 変更されていない

    def test_delete_person(self, person_crud, db_session):
        """人物削除のテスト"""
        person_data = PersonTestData.create_person_data(
            ssid="test_person_005",
            full_name="上杉謙信",
            description="越後の龍",
        )
        created_person = person_crud.create(db_session, obj_in=person_data)

        success = person_crud.remove(db_session, id=cast(int, created_person.id))
        assert success is True

        deleted_person = person_crud.get(db_session, cast(int, created_person.id))
        assert deleted_person is None

    def test_get_person_not_found(self, person_crud, db_session):
        """存在しない人物の取得テスト"""
        person = person_crud.get(db_session, 999)
        assert person is None

    def test_get_person_by_ssid_not_found(self, person_crud, db_session):
        """存在しないSSIDでの人物取得テスト"""
        person = person_crud.get_by_ssid(db_session, "non_existent_ssid")
        assert person is None

    def test_update_person_not_found(self, person_crud, db_session):
        """存在しない人物の更新テスト"""
        update_data = PersonUpdate(description="更新テスト")
        updated_person = person_crud.update(db_session, id=999, obj_in=update_data)
        assert updated_person is None

    def test_delete_person_not_found(self, person_crud, db_session):
        """存在しない人物の削除テスト"""
        success = person_crud.remove(db_session, id=999)
        assert success is False

    def test_update_person_partial(self, person_crud, db_session):
        """人物の部分更新テスト"""
        person_data = PersonTestData.create_person_data(
            ssid="test_person_006",
            full_name="明智光秀",
            description="織田信長の家臣",
        )
        created_person = person_crud.create(db_session, obj_in=person_data)

        # 部分更新（descriptionのみ）
        update_data = PersonUpdate(description="本能寺の変を起こした武将")
        updated_person = person_crud.update(db_session, id=cast(int, created_person.id), obj_in=update_data)

        assert updated_person is not None
        assert updated_person.description == "本能寺の変を起こした武将"
        assert updated_person.full_name == "明智光秀"  # 変更されていない
        assert updated_person.ssid == "test_person_006"  # 変更されていない

    def test_update_person_with_none_values(self, person_crud, db_session):
        """None値を含む更新テスト"""
        person_data = PersonTestData.create_person_data(
            ssid="test_person_007",
            full_name="石田三成",
            description="豊臣秀吉の家臣",
            born_region="近江",
        )
        created_person = person_crud.create(db_session, obj_in=person_data)

        # None値を含む更新データ（現在の実装ではNone値は除外される）
        update_data = PersonUpdate(
            description="関ヶ原の戦いで西軍を率いた武将",
            born_region=None,
        )
        updated_person = person_crud.update(db_session, id=cast(int, created_person.id), obj_in=update_data)

        assert updated_person is not None
        assert updated_person.description == "関ヶ原の戦いで西軍を率いた武将"
        assert updated_person.born_region == "近江"  # None値は除外されるため変更されない
        assert updated_person.full_name == "石田三成"  # 変更されていない
