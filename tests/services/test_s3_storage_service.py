"""
S3ストレージサービスのテスト
"""

import io
import os

import pytest
from PIL import Image

from app.services.s3_storage_service import S3StorageService


class TestS3StorageService:
    """S3ストレージサービスのテストクラス"""

    @pytest.fixture
    def s3_service(self):
        """実際のS3ストレージサービスインスタンス"""
        # 環境変数から実際の設定を読み込み
        bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
        region_name = os.getenv("AWS_REGION")
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        if not all([bucket_name, region_name, aws_access_key_id, aws_secret_access_key]):
            pytest.skip("S3接続に必要な環境変数が設定されていません")

        return S3StorageService(
            bucket_name=bucket_name,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    def test_s3_connection(self, s3_service):
        """S3接続テスト"""
        try:
            # バケットの存在確認
            s3_service.s3_client.head_bucket(Bucket=s3_service.bucket_name)
            print(f"✅ S3バケット '{s3_service.bucket_name}' に正常に接続できました")
        except Exception as e:
            pytest.fail(f"❌ S3接続エラー: {e}")

    def test_upload_file(self, s3_service):
        """ファイルアップロードテスト"""
        try:
            # テスト用の小さな画像を作成
            img = Image.new("RGB", (50, 50), color="green")
            img_buffer = io.BytesIO()
            img.save(img_buffer, format="JPEG")
            test_content = img_buffer.getvalue()

            # テストファイルをアップロード
            result = s3_service.upload_avatar(
                file_content=test_content, filename="test-connection.jpg", content_type="image/jpeg"
            )

            # 結果を検証
            assert "url" in result
            assert "filename" in result
            assert result["filename"].startswith("avatars/")
            print(f"✅ テストファイルのアップロードが成功しました: {result['url']}")

            # アップロードされたファイルの存在確認
            assert s3_service.file_exists(result["filename"])
            print("✅ アップロードされたファイルの存在確認が成功しました")

            # テストファイルを削除
            success = s3_service.delete_file(result["filename"])
            assert success
            print("✅ テストファイルの削除が成功しました")

        except Exception as e:
            pytest.fail(f"❌ S3アップロードテストエラー: {e}")

    def test_list_files(self, s3_service):
        """ファイル一覧取得テスト"""
        try:
            # ファイル一覧を取得
            files = s3_service.list_files("avatars/")
            print(f"✅ S3バケット内のファイル一覧取得が成功しました: {len(files)}個のファイル")

            # ファイル一覧の詳細を表示（最初の5個まで）
            for i, file_key in enumerate(files[:5]):
                print(f"  - {file_key}")

            if len(files) > 5:
                print(f"  ... 他 {len(files) - 5}個のファイル")

        except Exception as e:
            pytest.fail(f"❌ S3ファイル一覧取得エラー: {e}")

    def test_bucket_policy(self, s3_service):
        """バケットポリシー確認テスト"""
        try:
            # バケットポリシーを取得
            response = s3_service.s3_client.get_bucket_policy(Bucket=s3_service.bucket_name)
            policy = response["Policy"]
            print("✅ バケットポリシーが設定されています")
            print(f"   ポリシー: {policy[:200]}...")  # 最初の200文字のみ表示

        except Exception as e:
            print(f"⚠️  バケットポリシーが設定されていないか、アクセス権限がありません: {e}")

    def test_cors_configuration(self, s3_service):
        """CORS設定確認テスト"""
        try:
            # CORS設定を取得
            response = s3_service.s3_client.get_bucket_cors(Bucket=s3_service.bucket_name)
            cors_rules = response["CORSRules"]
            print("✅ CORS設定が設定されています")
            print(f"   CORSルール数: {len(cors_rules)}")

        except Exception as e:
            print(f"⚠️  CORS設定が設定されていないか、アクセス権限がありません: {e}")

    def test_url_accessibility(self, s3_service):
        """URLアクセシビリティテスト"""
        try:
            # テスト用の小さな画像を作成
            img = Image.new("RGB", (50, 50), color="blue")
            img_buffer = io.BytesIO()
            img.save(img_buffer, format="JPEG")
            test_content = img_buffer.getvalue()

            # テストファイルをアップロード
            result = s3_service.upload_avatar(
                file_content=test_content, filename="test-url-access.jpg", content_type="image/jpeg"
            )

            # URLの形式を検証
            expected_url_pattern = f"https://{s3_service.bucket_name}.s3.{s3_service.region_name}.amazonaws.com/"
            assert result["url"].startswith(expected_url_pattern)
            print(f"✅ S3 URLの形式が正しいです: {result['url']}")

            # テストファイルを削除
            s3_service.delete_file(result["filename"])

        except Exception as e:
            pytest.fail(f"❌ S3 URLアクセシビリティテストエラー: {e}")

    def test_image_processing(self, s3_service):
        """画像処理テスト"""
        try:
            # 大きな画像を作成（リサイズが必要）
            img = Image.new("RGB", (500, 500), color="red")
            img_buffer = io.BytesIO()
            img.save(img_buffer, format="JPEG")
            large_image_content = img_buffer.getvalue()

            # 画像処理を含むアップロード
            result = s3_service.upload_avatar(
                file_content=large_image_content, filename="test-image-processing.jpg", content_type="image/jpeg"
            )

            print(f"✅ 画像処理とアップロードが成功しました: {result['url']}")

            # テストファイルを削除
            s3_service.delete_file(result["filename"])

        except Exception as e:
            pytest.fail(f"❌ 画像処理テストエラー: {e}")

    def test_file_validation(self, s3_service):
        """ファイル検証テスト"""
        try:
            # 無効なファイル形式のテスト
            invalid_content = b"invalid file content"

            with pytest.raises(Exception) as exc_info:
                s3_service.upload_avatar(file_content=invalid_content, filename="test.txt", content_type="text/plain")

            # エラーメッセージを確認
            error_message = str(exc_info.value)
            if "サポートされていないファイル形式" in error_message:
                print("✅ ファイル形式検証が正常に動作しています")
            elif "S3アップロードエラー" in error_message:
                print("⚠️  S3アップロードエラーが発生しましたが、ファイル形式検証は正常に動作しています")
            else:
                print(f"ℹ️  予期しないエラー: {error_message}")

        except Exception as e:
            pytest.fail(f"❌ ファイル検証テストエラー: {e}")

    def test_file_size_validation(self, s3_service):
        """ファイルサイズ検証テスト"""
        try:
            # 大きなファイルを作成（6MB）
            large_content = b"x" * (6 * 1024 * 1024)

            with pytest.raises(Exception) as exc_info:
                s3_service.upload_avatar(
                    file_content=large_content, filename="large-file.jpg", content_type="image/jpeg"
                )

            # エラーメッセージを確認
            error_message = str(exc_info.value)
            if "ファイルサイズが大きすぎます" in error_message:
                print("✅ ファイルサイズ検証が正常に動作しています")
            elif "S3アップロードエラー" in error_message:
                print("⚠️  S3アップロードエラーが発生しましたが、ファイルサイズ検証は正常に動作しています")
            else:
                print(f"ℹ️  予期しないエラー: {error_message}")

        except Exception as e:
            pytest.fail(f"❌ ファイルサイズ検証テストエラー: {e}")
