from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from .. import schemas
from ..dependencies.api_key_auth import verify_token
from ..services.s3_storage_service import S3StorageService

router = APIRouter(tags=["avatar"])


def get_s3_storage_service() -> S3StorageService:
    """
    S3ストレージサービスのインスタンスを取得

    Returns:
        S3StorageService: S3ストレージサービスのインスタンス
    """
    return S3StorageService()


@router.post("/upload/avatar", response_model=schemas.AvatarUploadResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    api_key=Depends(verify_token),
    s3_storage_service: S3StorageService = Depends(get_s3_storage_service),
):
    """
    アバター画像アップロード（S3）

    認証済みユーザーがアバター画像をS3にアップロードできます。
    画像は自動的にリサイズされ、最適化されます。
    """
    try:
        # ファイル名の検証
        if not file.filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ファイル名が指定されていません")

        # コンテンツタイプの検証
        if not file.content_type:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="コンテンツタイプが指定されていません")

        # ファイル内容を読み込み
        file_content = await file.read()

        # S3にアップロード
        result = s3_storage_service.upload_avatar(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type,
        )

        return schemas.AvatarUploadResponse(**result)

    except HTTPException:
        # HTTPExceptionはそのまま再送出
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="アップロード処理中にエラーが発生しました"
        )


@router.delete("/upload/avatar/{filename}")
async def delete_avatar(
    filename: str,
    api_key=Depends(verify_token),
    s3_storage_service: S3StorageService = Depends(get_s3_storage_service),
):
    """
    アバター画像削除（S3）

    認証済みユーザーがS3からアバター画像を削除できます。
    """
    try:
        # ファイルキーを構築
        file_key = f"avatars/{filename}"

        # ファイルが存在するかチェック
        if not s3_storage_service.file_exists(file_key):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="指定されたファイルが見つかりません")

        # S3から削除
        success = s3_storage_service.delete_file(file_key)

        if success:
            return {"message": "ファイルが正常に削除されました"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="ファイル削除に失敗しました")

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="ファイル削除処理中にエラーが発生しました"
        )
