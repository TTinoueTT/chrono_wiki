"""
AWS S3ストレージサービス

画像ファイルのS3へのアップロード、ダウンロード、削除機能を提供します。
"""

import io
import os
import uuid
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException, status
from PIL import Image


class S3StorageService:
    """AWS S3ストレージサービス"""

    def __init__(
        self,
        bucket_name: str = "",
        region_name: str = "",
        aws_access_key_id: str = "",
        aws_secret_access_key: str = "",
    ):
        """
        初期化

        Args:
            bucket_name: S3バケット名（環境変数から取得）
            region_name: AWSリージョン（環境変数から取得）
            aws_access_key_id: AWSアクセスキー（環境変数から取得）
            aws_secret_access_key: AWSシークレットキー（環境変数から取得）
        """
        self.bucket_name = os.getenv("AWS_S3_BUCKET_NAME") or ""
        self.region_name = os.getenv("AWS_REGION", "us-east-1")
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID") or ""
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY") or ""

        if not self.bucket_name:
            raise ValueError("AWS_S3_BUCKET_NAME environment variable is required")

        # S3クライアントを初期化
        self.s3_client = boto3.client(
            "s3",
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

        # 許可された画像拡張子
        self.allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

        # 最大ファイルサイズ（5MB）
        self.max_file_size = 5 * 1024 * 1024

    def upload_avatar(self, file_content: bytes, filename: str, content_type: str) -> dict:
        """
        アバター画像をS3にアップロード

        Args:
            file_content: ファイルの内容
            filename: ファイル名
            content_type: コンテンツタイプ

        Returns:
            dict: アップロード結果（url, filename）

        Raises:
            HTTPException: アップロードエラー時
        """
        try:
            # ファイルサイズチェック
            if len(file_content) > self.max_file_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"ファイルサイズが大きすぎます。最大{self.max_file_size // (1024*1024)}MBまで",
                )

            # ファイル拡張子チェック
            file_extension = Path(filename).suffix.lower()
            if file_extension not in self.allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"サポートされていないファイル形式です。許可: {', '.join(self.allowed_extensions)}",
                )

            # 画像の検証とリサイズ
            processed_content = self._process_image(file_content, file_extension)

            # ユニークなファイル名を生成
            unique_filename = f"avatars/{uuid.uuid4()}{file_extension}"

            # S3にアップロード
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=processed_content,
                ContentType=content_type,
                CacheControl="max-age=31536000",  # 1年間キャッシュ
            )

            # URLを生成
            url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{unique_filename}"

            return {"url": url, "filename": unique_filename}

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchBucket":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="S3バケットが見つかりません"
                )
            elif error_code == "AccessDenied":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="S3アクセス権限がありません"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"S3アップロードエラー: {error_code}"
                )
        except NoCredentialsError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AWS認証情報が設定されていません"
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="ファイルアップロードに失敗しました"
            )

    def download_file(self, key: str) -> Optional[bytes]:
        """
        ファイルをS3からダウンロード

        Args:
            key: S3オブジェクトキー

        Returns:
            Optional[bytes]: ファイル内容、存在しない場合はNone
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            raise

    def delete_file(self, key: str) -> bool:
        """
        ファイルをS3から削除

        Args:
            key: S3オブジェクトキー

        Returns:
            bool: 削除成功時True
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False

    def file_exists(self, key: str) -> bool:
        """
        ファイルがS3に存在するかチェック

        Args:
            key: S3オブジェクトキー

        Returns:
            bool: 存在する場合True
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False

    def get_file_url(self, key: str) -> str:
        """
        ファイルの公開URLを取得

        Args:
            key: S3オブジェクトキー

        Returns:
            str: ファイルの公開URL
        """
        return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{key}"

    def _process_image(self, file_content: bytes, file_extension: str) -> bytes:
        """
        画像を処理（検証とリサイズ）

        Args:
            file_content: 画像ファイルの内容
            file_extension: ファイル拡張子

        Returns:
            bytes: 処理された画像データ

        Raises:
            HTTPException: 画像処理エラー時
        """
        try:
            # PILで画像を開く
            with Image.open(io.BytesIO(file_content)) as img:
                # 画像形式の検証
                img.verify()

                # 画像を再度開いてリサイズ処理
                with Image.open(io.BytesIO(file_content)) as img:
                    # RGBAの場合はRGBに変換
                    if img.mode in ("RGBA", "LA", "P"):
                        img = img.convert("RGB")

                    # アバター用にリサイズ（最大300x300）
                    img.thumbnail((300, 300), Image.Resampling.LANCZOS)

                    # 画像をバイトデータに変換
                    output_buffer = io.BytesIO()

                    # 拡張子に応じて保存形式を決定
                    if file_extension.lower() in [".jpg", ".jpeg"]:
                        img.save(output_buffer, format="JPEG", optimize=True, quality=85)
                    elif file_extension.lower() == ".png":
                        img.save(output_buffer, format="PNG", optimize=True)
                    elif file_extension.lower() == ".gif":
                        img.save(output_buffer, format="GIF", optimize=True)
                    elif file_extension.lower() == ".webp":
                        img.save(output_buffer, format="WEBP", quality=85)
                    else:
                        # デフォルトはJPEG
                        img.save(output_buffer, format="JPEG", optimize=True, quality=85)

                    output_buffer.seek(0)
                    return output_buffer.getvalue()

        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="無効な画像ファイルです")

    def list_files(self, prefix: str = "") -> list:
        """
        指定されたプレフィックスのファイル一覧を取得

        Args:
            prefix: ファイルキーのプレフィックス

        Returns:
            list: ファイルキーのリスト
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)

            if "Contents" in response:
                return [obj["Key"] for obj in response["Contents"]]
            return []

        except ClientError:
            return []


# グローバルインスタンス
s3_storage_service = S3StorageService()
