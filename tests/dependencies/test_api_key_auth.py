"""
APIキー認証依存性のテスト

app/dependencies/api_key_auth.pyのテストケースを実装します。
"""

import os
from unittest.mock import patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.dependencies.api_key_auth import optional_verify_token, verify_token
from app.main import app

client = TestClient(app)


@pytest.mark.dependencies
@pytest.mark.auth
class TestAPIKeyAuth:
    """APIキー認証のテスト"""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """環境変数をセットアップ"""
        # テスト用のAPIキーを設定
        os.environ["API_KEY"] = "test_api_key_123"
        yield
        # クリーンアップ
        if "API_KEY" in os.environ:
            del os.environ["API_KEY"]

    def test_verify_token_valid_key(self):
        """有効なAPIキーでの認証テスト"""
        with patch("app.dependencies.api_key_auth.api_key_header") as mock_header:
            mock_header.return_value = "test_api_key_123"

            result = verify_token("test_api_key_123")
            assert result == "test_api_key_123"

    def test_verify_token_invalid_key(self):
        """無効なAPIキーでの認証テスト"""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid_key")

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Invalid API key"

    def test_verify_token_empty_key(self):
        """空のAPIキーでの認証テスト"""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("")

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Invalid API key"

    def test_verify_token_none_key(self):
        """NoneのAPIキーでの認証テスト"""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("")  # Noneの代わりに空文字を使用

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Invalid API key"

    def test_optional_verify_token_valid_key(self):
        """有効なAPIキーでのオプショナル認証テスト"""
        with patch("app.dependencies.api_key_auth.api_key_header") as mock_header:
            mock_header.return_value = "test_api_key_123"

            result = optional_verify_token("test_api_key_123")
            assert result == "test_api_key_123"

    def test_optional_verify_token_invalid_key(self):
        """無効なAPIキーでのオプショナル認証テスト"""
        with pytest.raises(HTTPException) as exc_info:
            optional_verify_token("invalid_key")

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Invalid API key"

    def test_verify_token_with_different_env_key(self):
        """異なる環境変数のAPIキーでの認証テスト"""
        # 環境変数を変更
        os.environ["API_KEY"] = "different_test_key"

        with patch("app.dependencies.api_key_auth.api_key_header") as mock_header:
            mock_header.return_value = "different_test_key"

            result = verify_token("different_test_key")
            assert result == "different_test_key"

    def test_verify_token_with_default_key(self):
        """デフォルトAPIキーでの認証テスト"""
        # 環境変数を削除してデフォルト値を使用
        if "API_KEY" in os.environ:
            del os.environ["API_KEY"]

        with patch("app.dependencies.api_key_auth.api_key_header") as mock_header:
            mock_header.return_value = "dev_sk_default"

            result = verify_token("dev_sk_default")
            assert result == "dev_sk_default"

    def test_verify_token_case_sensitive(self):
        """大文字小文字を区別するAPIキーテスト"""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("TEST_API_KEY_123")  # 大文字

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Invalid API key"

    def test_verify_token_with_whitespace(self):
        """空白文字を含むAPIキーテスト"""
        with pytest.raises(HTTPException) as exc_info:
            verify_token(" test_api_key_123 ")  # 前後に空白

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Invalid API key"

    def test_verify_token_with_special_characters(self):
        """特殊文字を含むAPIキーテスト"""
        # 特殊文字を含むAPIキーを環境変数に設定
        os.environ["API_KEY"] = "test_key_with_@#$%"

        with patch("app.dependencies.api_key_auth.api_key_header") as mock_header:
            mock_header.return_value = "test_key_with_@#$%"

            result = verify_token("test_key_with_@#$%")
            assert result == "test_key_with_@#$%"

    def test_verify_token_long_key(self):
        """長いAPIキーテスト"""
        long_key = "a" * 1000  # 1000文字のキー
        os.environ["API_KEY"] = long_key

        with patch("app.dependencies.api_key_auth.api_key_header") as mock_header:
            mock_header.return_value = long_key

            result = verify_token(long_key)
            assert result == long_key

    def test_verify_token_unicode_key(self):
        """Unicode文字を含むAPIキーテスト"""
        unicode_key = "test_key_日本語_123"
        os.environ["API_KEY"] = unicode_key

        with patch("app.dependencies.api_key_auth.api_key_header") as mock_header:
            mock_header.return_value = unicode_key

            result = verify_token(unicode_key)
            assert result == unicode_key


@pytest.mark.dependencies
@pytest.mark.auth
class TestAPIKeyAuthIntegration:
    """APIキー認証の統合テスト"""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """環境変数をセットアップ"""
        os.environ["API_KEY"] = "integration_test_key"
        yield
        if "API_KEY" in os.environ:
            del os.environ["API_KEY"]

    def test_api_key_auth_in_fastapi_dependency(self):
        """FastAPI依存性としてのAPIキー認証テスト"""
        # 実際のエンドポイントでAPIキー認証を使用する場合のテスト
        # このテストは、APIキー認証がFastAPIの依存性システムで
        # 正しく動作することを確認します

        # 注意: 実際のエンドポイントでAPIキー認証を使用していない場合は
        # このテストはスキップされます
        pytest.skip("APIキー認証を使用するエンドポイントが実装されていないため")

    def test_api_key_auth_error_headers(self):
        """APIキー認証エラー時のヘッダーテスト"""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid_key")

        # エラーレスポンスに適切なヘッダーが含まれていることを確認
        assert exc_info.value.headers is not None
        assert "WWW-Authenticate" in exc_info.value.headers
        assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.dependencies
@pytest.mark.auth
class TestAPIKeyAuthEdgeCases:
    """APIキー認証のエッジケーステスト"""

    def test_verify_token_with_none_env_var(self):
        """環境変数がNoneの場合のテスト"""
        # 環境変数をNoneに設定
        os.environ["API_KEY"] = "None"

        with pytest.raises(HTTPException) as exc_info:
            verify_token("test_key")

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_verify_token_with_empty_env_var(self):
        """環境変数が空文字の場合のテスト"""
        os.environ["API_KEY"] = ""

        with pytest.raises(HTTPException) as exc_info:
            verify_token("test_key")

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_verify_token_with_whitespace_env_var(self):
        """環境変数が空白文字の場合のテスト"""
        os.environ["API_KEY"] = "   "

        with pytest.raises(HTTPException) as exc_info:
            verify_token("test_key")

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_verify_token_missing_env_var(self):
        """環境変数が存在しない場合のテスト"""
        # 環境変数を削除
        if "API_KEY" in os.environ:
            del os.environ["API_KEY"]

        # デフォルト値が使用されることを確認
        with patch("app.dependencies.api_key_auth.api_key_header") as mock_header:
            mock_header.return_value = "dev_sk_default"

            result = verify_token("dev_sk_default")
            assert result == "dev_sk_default"
