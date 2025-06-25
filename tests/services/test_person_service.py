# type: ignore

"""
人物サービスのテスト

人物サービスのビジネスロジックをテストします。
"""

from datetime import date

import pytest

from app import schemas
from app.services import PersonService


@pytest.mark.service
class TestPersonService:
    """人物サービスのテスト"""

    def test_create_person_success(self, person_service: PersonService, db_session):
        """人物作成の成功テスト"""
        person_data = schemas.PersonCreate(
            ssid="test_person_001",
            full_name="織田信長",
            display_name="信長",
            search_name="おだのぶなが",
            birth_date=date(1534, 6, 23),
            death_date=date(1582, 6, 21),
            born_country="日本",
            born_region="尾張国",
            description="戦国時代の武将",
        )

        person = person_service.create_person(db_session, person_data)

        assert person.id is not None
        assert person.ssid == "test_person_001"
        assert person.full_name == "織田信長"
        assert person.birth_date == date(1534, 6, 23)

    def test_create_person_duplicate_ssid(self, person_service: PersonService, db_session):
        """重複SSIDでの人物作成失敗テスト"""
        person_data = schemas.PersonCreate(
            ssid="test_person_duplicate",
            full_name="テスト人物",
            display_name="テスト",
            search_name="てすとじんぶつ",
            birth_date=date(1534, 6, 23),
            born_country="日本",
        )

        # 最初の作成は成功
        person_service.create_person(db_session, person_data)

        # 2回目の作成は失敗
        with pytest.raises(
            ValueError,
            match="SSID 'test_person_duplicate' is already registered",
        ):
            person_service.create_person(db_session, person_data)

    def test_validate_person_data_success(self, person_service: PersonService):
        """人物データバリデーション成功テスト"""
        person_data = schemas.PersonCreate(
            ssid="test_person_valid",
            full_name="有効な人物",
            display_name="有効",
            search_name="ゆうこうなじんぶつ",
            birth_date=date(1534, 6, 23),
            born_country="日本",
        )

        # バリデーションが成功することを確認
        person_service.validate_person_data(person_data)

    def test_validate_person_data_missing_full_name(self, person_service: PersonService):
        """フルネーム不足でのバリデーション失敗テスト"""
        person_data = schemas.PersonCreate(
            ssid="test_person_no_name",
            full_name="",  # 空のフルネーム
            display_name="テスト",
            search_name="てすと",
            birth_date=date(1534, 6, 23),
            born_country="日本",
        )

        with pytest.raises(ValueError, match="Full name is required"):
            person_service.validate_person_data(person_data)

    def test_validate_person_data_missing_ssid(self, person_service: PersonService):
        """SSID不足でのバリデーション失敗テスト"""
        person_data = schemas.PersonCreate(
            ssid="",  # 空のSSID
            full_name="テスト人物",
            display_name="テスト",
            search_name="てすとじんぶつ",
            birth_date=date(1534, 6, 23),
            born_country="日本",
        )

        with pytest.raises(ValueError, match="SSID is required"):
            person_service.validate_person_data(person_data)

    def test_validate_person_data_invalid_date_range(self, person_service: PersonService):
        """無効な日付範囲でのバリデーション失敗テスト"""
        person_data = schemas.PersonCreate(
            ssid="test_person_invalid_dates",
            full_name="無効な日付の人物",
            display_name="無効",
            search_name="むこうなにちづけのじんぶつ",
            birth_date=date(1582, 6, 21),  # 生年月日が没年月日より後
            death_date=date(1534, 6, 23),
            born_country="日本",
        )

        with pytest.raises(ValueError, match="Birth date cannot be after death date"):
            person_service.validate_person_data(person_data)

    def test_get_person_success(self, person_service: PersonService, db_session):
        """人物取得の成功テスト"""
        # 人物を作成
        person_data = schemas.PersonCreate(
            ssid="test_person_get",
            full_name="取得テスト人物",
            display_name="取得",
            search_name="しゅとくてすとじんぶつ",
            birth_date=date(1534, 6, 23),
            born_country="日本",
        )
        created_person = person_service.create_person(db_session, person_data)

        # 人物を取得
        retrieved_person = person_service.get_person(db_session, created_person.id)

        assert retrieved_person is not None
        assert retrieved_person.ssid == "test_person_get"
        assert retrieved_person.full_name == "取得テスト人物"

    def test_get_person_not_found(self, person_service: PersonService, db_session):
        """存在しない人物の取得テスト"""
        person = person_service.get_person(db_session, 999)
        assert person is None

    def test_get_person_by_ssid_success(self, person_service: PersonService, db_session):
        """SSIDでの人物取得成功テスト"""
        # 人物を作成
        person_data = schemas.PersonCreate(
            ssid="test_person_ssid",
            full_name="SSID取得テスト",
            display_name="SSID",
            search_name="えすえすあいでぃしゅとくてすと",
            birth_date=date(1534, 6, 23),
            born_country="日本",
        )
        person_service.create_person(db_session, person_data)

        # SSIDで取得
        retrieved_person = person_service.get_person_by_ssid(db_session, "test_person_ssid")

        assert retrieved_person is not None
        assert retrieved_person.ssid == "test_person_ssid"

    def test_get_person_by_ssid_not_found(self, person_service: PersonService, db_session):
        """存在しないSSIDでの人物取得テスト"""
        person = person_service.get_person_by_ssid(db_session, "non_existent_ssid")
        assert person is None

    def test_update_person_success(self, person_service: PersonService, db_session):
        """人物更新の成功テスト"""
        # 人物を作成
        person_data = schemas.PersonCreate(
            ssid="test_person_update",
            full_name="更新前の名前",
            display_name="更新前",
            search_name="こうしんまえのなまえ",
            birth_date=date(1534, 6, 23),
            born_country="日本",
        )
        created_person = person_service.create_person(db_session, person_data)

        # 人物を更新
        update_data = schemas.PersonUpdate(
            full_name="更新後の名前",
            description="更新された説明",
        )
        updated_person = person_service.update_person(db_session, created_person.id, update_data)

        assert updated_person is not None
        assert updated_person.full_name == "更新後の名前"
        assert updated_person.description == "更新された説明"
        assert updated_person.ssid == "test_person_update"  # 変更されていない

    def test_update_person_not_found(self, person_service: PersonService, db_session):
        """存在しない人物の更新テスト"""
        update_data = schemas.PersonUpdate(full_name="更新テスト")
        updated_person = person_service.update_person(db_session, 999, update_data)
        assert updated_person is None

    def test_delete_person_success(self, person_service: PersonService, db_session):
        """人物削除の成功テスト"""
        # 人物を作成
        person_data = schemas.PersonCreate(
            ssid="test_person_delete",
            full_name="削除テスト人物",
            display_name="削除",
            search_name="さくじょてすとじんぶつ",
            birth_date=date(1534, 6, 23),
            born_country="日本",
        )
        created_person = person_service.create_person(db_session, person_data)

        # 人物を削除
        success = person_service.delete_person(db_session, created_person.id)
        assert success is True

        # 削除確認
        deleted_person = person_service.get_person(db_session, created_person.id)
        assert deleted_person is None

    def test_delete_person_not_found(self, person_service: PersonService, db_session):
        """存在しない人物の削除テスト"""
        success = person_service.delete_person(db_session, 999)
        assert success is False

    def test_get_persons_by_birth_year(self, person_service: PersonService, db_session):
        """生年での人物検索テスト"""
        # 複数の人物を作成
        person_data1 = schemas.PersonCreate(
            ssid="test_person_1534_1",
            full_name="1534年生まれ1",
            display_name="1534-1",
            search_name="せんごひゃくさんじゅうよんねんうまれいち",
            birth_date=date(1534, 6, 23),
            born_country="日本",
        )
        person_data2 = schemas.PersonCreate(
            ssid="test_person_1534_2",
            full_name="1534年生まれ2",
            display_name="1534-2",
            search_name="せんごひゃくさんじゅうよんねんうまれに",
            birth_date=date(1534, 8, 15),
            born_country="日本",
        )
        person_data3 = schemas.PersonCreate(
            ssid="test_person_1537",
            full_name="1537年生まれ",
            display_name="1537",
            search_name="せんごひゃくさんじゅうななねんうまれ",
            birth_date=date(1537, 3, 17),
            born_country="日本",
        )

        person_service.create_person(db_session, person_data1)
        person_service.create_person(db_session, person_data2)
        person_service.create_person(db_session, person_data3)

        # 1534年生まれを検索
        persons_1534 = person_service.get_persons_by_birth_year(db_session, 1534)
        assert len(persons_1534) == 2
        assert all(p.birth_date.year == 1534 for p in persons_1534)

        # 1537年生まれを検索
        persons_1537 = person_service.get_persons_by_birth_year(db_session, 1537)
        assert len(persons_1537) == 1
        assert persons_1537[0].birth_date.year == 1537

    def test_get_persons_by_country(self, person_service: PersonService, db_session):
        """出生国での人物検索テスト"""
        # 複数の人物を作成
        person_data1 = schemas.PersonCreate(
            ssid="test_person_japan_1",
            full_name="日本の人物1",
            display_name="日本1",
            search_name="にほんのじんぶついち",
            birth_date=date(1534, 6, 23),
            born_country="日本",
        )
        person_data2 = schemas.PersonCreate(
            ssid="test_person_japan_2",
            full_name="日本の人物2",
            display_name="日本2",
            search_name="にほんのじんぶつに",
            birth_date=date(1537, 3, 17),
            born_country="日本",
        )
        person_data3 = schemas.PersonCreate(
            ssid="test_person_china",
            full_name="中国の人物",
            display_name="中国",
            search_name="ちゅうごくのじんぶつ",
            birth_date=date(1500, 1, 1),
            born_country="中国",
        )

        person_service.create_person(db_session, person_data1)
        person_service.create_person(db_session, person_data2)
        person_service.create_person(db_session, person_data3)

        # 日本の人物を検索
        japanese_persons = person_service.get_persons_by_country(db_session, "日本")
        assert len(japanese_persons) == 2
        assert all(p.born_country.lower() == "日本" for p in japanese_persons)

        # 中国の人物を検索
        chinese_persons = person_service.get_persons_by_country(db_session, "中国")
        assert len(chinese_persons) == 1
        assert chinese_persons[0].born_country.lower() == "中国"

    def test_get_persons_pagination(self, person_service: PersonService, db_session):
        """人物一覧のページネーションテスト"""
        # 複数の人物を作成
        for i in range(5):
            person_data = schemas.PersonCreate(
                ssid=f"test_person_pag_{i}",
                full_name=f"ページネーションテスト{i}",
                display_name=f"ページ{i}",
                search_name=f"ぺーじねーしょんてすと{i}",
                birth_date=date(1500 + i, 1, 1),
                born_country="日本",
            )
            person_service.create_person(db_session, person_data)

        # 最初の2件を取得
        persons_page1 = person_service.get_persons(db_session, skip=0, limit=2)
        assert len(persons_page1) == 2

        # 次の2件を取得
        persons_page2 = person_service.get_persons(db_session, skip=2, limit=2)
        assert len(persons_page2) == 2

        # 最後の1件を取得
        persons_page3 = person_service.get_persons(db_session, skip=4, limit=2)
        assert len(persons_page3) == 1

        # ページ間で重複がないことを確認
        page1_ids = {p.id for p in persons_page1}
        page2_ids = {p.id for p in persons_page2}
        page3_ids = {p.id for p in persons_page3}

        assert page1_ids.isdisjoint(page2_ids)
        assert page2_ids.isdisjoint(page3_ids)
        assert page1_ids.isdisjoint(page3_ids)
