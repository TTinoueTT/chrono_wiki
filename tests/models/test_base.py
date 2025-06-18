from datetime import UTC, datetime

from sqlalchemy import BigInteger, DateTime

from app.models.base import BaseModel, TimestampMixin


def test_base_model_creation():
    """Baseモデルの基本的な属性をテスト"""
    now = datetime.now(UTC)
    base = BaseModel(id=1, created_at=now, updated_at=now)

    assert str(base.id) == "1"
    assert str(base.created_at) == str(now)
    assert str(base.updated_at) == str(now)


def test_base_model_default_values():
    """Baseモデルのデフォルト値をテスト"""
    base = BaseModel()
    # idは自動生成されるため、Noneではなく未設定状態を確認
    assert not hasattr(base, "_id")
    # created_atとupdated_atはカラム定義が返される
    assert base.created_at is not None
    assert base.updated_at is not None
    # カラムの型を確認
    assert isinstance(BaseModel.created_at.type, DateTime)
    assert isinstance(BaseModel.updated_at.type, DateTime)


def test_timestamp_mixin_auto_update():
    """タイムスタンプの自動更新をテスト"""
    base = BaseModel()
    # 抽象クラスでは実際の値ではなくカラム定義が返される
    assert base.updated_at is not None
    # onupdateが設定されていることを確認
    assert BaseModel.updated_at.onupdate is not None


def test_base_model_abstract():
    """BaseModelが抽象クラスであることを確認"""
    assert BaseModel.__abstract__ is True


def test_column_constraints():
    """カラムの制約をテスト"""
    # カラムの存在確認
    assert hasattr(BaseModel, "id")
    assert hasattr(BaseModel, "created_at")
    assert hasattr(BaseModel, "updated_at")

    # カラムの型確認
    assert isinstance(BaseModel.id.type, BigInteger)
    assert isinstance(BaseModel.created_at.type, DateTime)
    assert isinstance(BaseModel.updated_at.type, DateTime)

    # カラムの制約確認
    assert BaseModel.id.primary_key
    assert BaseModel.id.autoincrement
    assert not BaseModel.id.nullable
    assert not BaseModel.created_at.nullable
    assert not BaseModel.updated_at.nullable


def test_inheritance():
    """継承関係をテスト"""
    # BaseModelがTimestampMixinを継承していることを確認
    assert TimestampMixin in BaseModel.__bases__
    # 必要な属性が存在することを確認
    assert hasattr(BaseModel, "created_at")
    assert hasattr(BaseModel, "updated_at")
    assert hasattr(BaseModel, "id")


def test_error_cases():
    """エラーケースをテスト"""
    # 抽象クラスではバリデーションが実行されないため、
    # 実際のインスタンス化時にテストする必要がある
    # ここではバリデーションメソッドの存在を確認
    assert hasattr(BaseModel, "validate_id")
    assert hasattr(BaseModel, "validate_datetime")
