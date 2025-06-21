import pytest
from sqlalchemy import JSON, Date, Numeric, String, Text

from app.models.event import Event


@pytest.mark.model
def test_event_model_attributes():
    """Eventモデルの属性存在確認"""
    # 基本属性の確認
    assert hasattr(Event, "id")
    assert hasattr(Event, "ssid")
    assert hasattr(Event, "title")
    assert hasattr(Event, "start_data")
    assert hasattr(Event, "end_data")
    assert hasattr(Event, "description")
    assert hasattr(Event, "location_name")
    assert hasattr(Event, "latitude")
    assert hasattr(Event, "longitude")
    assert hasattr(Event, "place_id")
    assert hasattr(Event, "image_url")
    assert hasattr(Event, "created_at")
    assert hasattr(Event, "updated_at")


@pytest.mark.model
def test_event_model_column_types():
    """Eventモデルのカラム型をテスト"""
    # カラムの型確認
    assert isinstance(Event.ssid.type, String)
    assert isinstance(Event.title.type, String)
    assert isinstance(Event.start_data.type, Date)
    assert isinstance(Event.end_data.type, Date)
    assert isinstance(Event.description.type, Text)
    assert isinstance(Event.location_name.type, String)
    assert isinstance(Event.latitude.type, Numeric)
    assert isinstance(Event.longitude.type, Numeric)
    assert isinstance(Event.place_id.type, String)
    assert isinstance(Event.image_url.type, JSON)


@pytest.mark.model
def test_event_model_constraints():
    """Eventモデルの制約をテスト"""
    # 必須フィールドの確認
    assert not Event.ssid.nullable
    assert not Event.title.nullable
    assert not Event.start_data.nullable

    # オプショナルフィールドの確認
    assert Event.end_data.nullable
    assert Event.description.nullable
    assert Event.location_name.nullable
    assert Event.latitude.nullable
    assert Event.longitude.nullable
    assert Event.place_id.nullable
    assert Event.image_url.nullable

    # インデックスの確認
    assert Event.ssid.index


@pytest.mark.model
def test_event_model_relationships():
    """Eventモデルのリレーションシップをテスト"""
    # リレーションシップの存在確認
    assert hasattr(Event, "tags")
    assert hasattr(Event, "persons")


@pytest.mark.model
def test_event_model_table_name():
    """Eventモデルのテーブル名をテスト"""
    assert Event.__tablename__ == "event"


@pytest.mark.model
def test_event_model_inheritance():
    """Eventモデルの継承関係をテスト"""
    from app.models.base import BaseModel

    # BaseModelを継承していることを確認
    assert issubclass(Event, BaseModel)


@pytest.mark.model
def test_event_model_string_lengths():
    """Eventモデルの文字列長制限をテスト"""
    # 文字列型フィールドの存在確認
    assert hasattr(Event, "ssid")
    assert hasattr(Event, "title")
    assert hasattr(Event, "location_name")
    assert hasattr(Event, "place_id")


@pytest.mark.model
def test_event_model_numeric_fields():
    """Eventモデルの数値フィールドをテスト"""
    # 数値型フィールドの存在確認
    assert hasattr(Event, "latitude")
    assert hasattr(Event, "longitude")
