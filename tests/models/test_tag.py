import pytest
from sqlalchemy import String, Text

from app.models.tag import Tag


@pytest.mark.model
def test_tag_model_attributes():
    """Tagモデルの属性存在確認"""
    # 基本属性の確認
    assert hasattr(Tag, "id")
    assert hasattr(Tag, "ssid")
    assert hasattr(Tag, "name")
    assert hasattr(Tag, "description")
    assert hasattr(Tag, "created_at")
    assert hasattr(Tag, "updated_at")


@pytest.mark.model
def test_tag_model_column_types():
    """Tagモデルのカラム型をテスト"""
    # カラムの型確認
    assert isinstance(Tag.ssid.type, String)
    assert isinstance(Tag.name.type, String)
    assert isinstance(Tag.description.type, Text)


@pytest.mark.model
def test_tag_model_constraints():
    """Tagモデルの制約をテスト"""
    # 必須フィールドの確認
    assert not Tag.ssid.nullable
    assert not Tag.name.nullable

    # オプショナルフィールドの確認
    assert Tag.description.nullable

    # インデックスの確認
    assert Tag.ssid.index


@pytest.mark.model
def test_tag_model_relationships():
    """Tagモデルのリレーションシップをテスト"""
    # リレーションシップの存在確認
    assert hasattr(Tag, "persons")
    assert hasattr(Tag, "events")


@pytest.mark.model
def test_tag_model_table_name():
    """Tagモデルのテーブル名をテスト"""
    assert Tag.__tablename__ == "tag"


@pytest.mark.model
def test_tag_model_inheritance():
    """Tagモデルの継承関係をテスト"""
    from app.models.base import BaseModel

    # BaseModelを継承していることを確認
    assert issubclass(Tag, BaseModel)


@pytest.mark.model
def test_tag_model_string_fields():
    """Tagモデルの文字列フィールドをテスト"""
    # 文字列型フィールドの存在確認
    assert hasattr(Tag, "ssid")
    assert hasattr(Tag, "name")
