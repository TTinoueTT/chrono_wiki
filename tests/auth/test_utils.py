import os
from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.auth import utils


# テスト用の環境変数をセット
@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test_secret")
    monkeypatch.setenv("ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1")
    monkeypatch.setenv("REFRESH_TOKEN_EXPIRE_DAYS", "1")
    # reload utils to re-import env vars
    import importlib

    importlib.reload(utils)
    yield


def test_get_password_hash_and_verify_password():
    """
    [観点]
    - get_password_hash: パスワードがハッシュ化されること
    - verify_password: 正しいパスワードでTrue、誤ったパスワードでFalseになること
    - ハッシュ値はstr型であること
    - ハッシュ値から元のパスワードが推測できないこと（不可逆性はpasslib任せ）
    """
    password = "testpassword123"
    hashed = utils.get_password_hash(password)
    assert isinstance(hashed, str)  # ハッシュ値はstr型
    assert utils.verify_password(password, hashed)  # 正しいパスワードでTrue
    assert not utils.verify_password("wrongpassword", hashed)  # 間違いパスワードでFalse


def test_create_and_verify_access_token():
    """
    [観点]
    - create_access_token: JWT文字列が返ること
    - verify_token: 正常なトークンでpayloadが取得できること
    - payloadにsub/email/type/expが正しく含まれること
    - typeが'access'であること
    """
    data = {"sub": "user_id", "email": "test@example.com"}
    token = utils.create_access_token(data)
    assert isinstance(token, str)  # JWT文字列であること
    payload = utils.verify_token(token)
    assert payload is not None  # トークンが有効
    assert payload["sub"] == "user_id"  # subが一致
    assert payload["email"] == "test@example.com"  # emailが一致
    assert payload["type"] == "access"  # typeがaccess
    assert "exp" in payload  # 有効期限が含まれる


def test_create_and_verify_refresh_token():
    """
    [観点]
    - create_refresh_token: JWT文字列が返ること
    - verify_token: 正常なトークンでpayloadが取得できること
    - payloadにsub/type/expが正しく含まれること
    - typeが'refresh'であること
    """
    data = {"sub": "user_id"}
    token = utils.create_refresh_token(data)
    assert isinstance(token, str)  # JWT文字列であること
    payload = utils.verify_token(token)
    assert payload is not None  # トークンが有効
    assert payload["sub"] == "user_id"  # subが一致
    assert payload["type"] == "refresh"  # typeがrefresh
    assert "exp" in payload  # 有効期限が含まれる


def test_verify_token_invalid():
    """
    [観点]
    - verify_token: 改ざんトークンや期限切れトークンでNoneが返ること
    - セキュリティ: 不正トークンを受け付けない
    """
    # 改ざんトークン
    invalid_token = "invalid.token.value"
    assert utils.verify_token(invalid_token) is None  # 不正トークンはNone

    # 有効期限切れトークン
    data = {"sub": "user_id"}
    expire = datetime.now(timezone.utc) - timedelta(minutes=1)
    payload = {**data, "exp": expire, "type": "access"}
    token = jwt.encode(payload, os.environ["SECRET_KEY"], algorithm=os.environ["ALGORITHM"])
    assert utils.verify_token(token) is None  # 期限切れトークンはNone


def test_get_token_expires_in():
    """
    [観点]
    - get_token_expires_in: 設定値（分）が秒換算で返ること
    - 返却値がint型であること
    """
    assert utils.get_token_expires_in() == 60  # 1分 * 60秒
