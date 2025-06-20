from sqlalchemy import Date, String, Text

from app.models.person import Person


def test_person_model_attributes():
    """Personモデルの属性存在確認"""
    # 基本属性の確認
    assert hasattr(Person, "id")
    assert hasattr(Person, "ssid")
    assert hasattr(Person, "full_name")
    assert hasattr(Person, "display_name")
    assert hasattr(Person, "search_name")
    assert hasattr(Person, "birth_date")
    assert hasattr(Person, "death_date")
    assert hasattr(Person, "born_country")
    assert hasattr(Person, "born_region")
    assert hasattr(Person, "description")
    assert hasattr(Person, "portrait_url")
    assert hasattr(Person, "created_at")
    assert hasattr(Person, "updated_at")


def test_person_model_column_types():
    """Personモデルのカラム型をテスト"""
    # カラムの型確認
    assert isinstance(Person.ssid.type, String)
    assert isinstance(Person.full_name.type, String)
    assert isinstance(Person.display_name.type, String)
    assert isinstance(Person.search_name.type, String)
    assert isinstance(Person.birth_date.type, Date)
    assert isinstance(Person.death_date.type, Date)
    assert isinstance(Person.born_country.type, String)
    assert isinstance(Person.born_region.type, String)
    assert isinstance(Person.description.type, Text)
    assert isinstance(Person.portrait_url.type, String)


def test_person_model_constraints():
    """Personモデルの制約をテスト"""
    # 必須フィールドの確認
    assert not Person.ssid.nullable
    assert not Person.full_name.nullable
    assert not Person.display_name.nullable
    assert not Person.search_name.nullable
    assert not Person.birth_date.nullable
    assert not Person.born_country.nullable

    # オプショナルフィールドの確認
    assert Person.death_date.nullable
    assert Person.born_region.nullable
    assert Person.description.nullable
    assert Person.portrait_url.nullable


def test_person_model_relationships():
    """Personモデルのリレーションシップをテスト"""
    # リレーションシップの存在確認
    assert hasattr(Person, "tags")
    assert hasattr(Person, "events")


def test_person_model_table_name():
    """Personモデルのテーブル名をテスト"""
    assert Person.__tablename__ == "person"


def test_person_model_inheritance():
    """Personモデルの継承関係をテスト"""
    from app.models.base import BaseModel

    # BaseModelを継承していることを確認
    assert issubclass(Person, BaseModel)
 