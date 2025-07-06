from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services import TagService

router = APIRouter(tags=["tags"])


def get_tag_service() -> TagService:
    """
    タグサービスのインスタンスを取得

    Returns:
        TagService: タグサービスのインスタンス
    """
    return TagService()


@router.post(
    "/tags/",
    response_model=schemas.Tag,
    status_code=status.HTTP_201_CREATED,
)
def create_tag(
    tag: schemas.TagCreate,
    db: Session = Depends(get_db),
    tag_service: TagService = Depends(get_tag_service),
):
    """
    タグを作成

    Args:
        tag: タグ作成データ
        db: データベースセッション
        tag_service: タグサービス（DI）

    Returns:
        作成されたタグ

    Raises:
        HTTPException: バリデーションエラーまたは重複エラーの場合
    """
    try:
        return tag_service.create_tag(db, tag)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/tags/", response_model=List[schemas.Tag])
def read_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tag_service: TagService = Depends(get_tag_service),
):
    """
    タグ一覧を取得

    Args:
        skip: スキップ数
        limit: 取得上限数
        db: データベースセッション
        tag_service: タグサービス（DI）

    Returns:
        タグのリスト
    """
    return tag_service.get_tags(db, skip=skip, limit=limit)


@router.get("/tags/{tag_id}", response_model=schemas.Tag)
def read_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    tag_service: TagService = Depends(get_tag_service),
):
    """
    タグを取得

    Args:
        tag_id: タグID
        db: データベースセッション
        tag_service: タグサービス（DI）

    Returns:
        タグデータ

    Raises:
        HTTPException: タグが見つからない場合
    """
    tag = tag_service.get_tag(db, tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
    return tag


@router.put("/tags/{tag_id}", response_model=schemas.Tag)
def update_tag(
    tag_id: int,
    tag: schemas.TagUpdate,
    db: Session = Depends(get_db),
    tag_service: TagService = Depends(get_tag_service),
):
    """
    タグを更新

    Args:
        tag_id: タグID
        tag: 更新データ
        db: データベースセッション
        tag_service: タグサービス（DI）

    Returns:
        更新されたタグデータ

    Raises:
        HTTPException: タグが見つからない場合またはバリデーションエラーの場合
    """
    try:
        updated_tag = tag_service.update_tag(db, tag_id, tag)
        if updated_tag is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found",
            )
        return updated_tag
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    tag_service: TagService = Depends(get_tag_service),
):
    """
    タグを削除

    Args:
        tag_id: タグID
        db: データベースセッション
        tag_service: タグサービス（DI）

    Raises:
        HTTPException: タグが見つからない場合
    """
    success = tag_service.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
