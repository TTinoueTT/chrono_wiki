from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services import TagService

router = APIRouter(prefix="/tags", tags=["tags"])

# サービスインスタンス
tag_service = TagService()


@router.post(
    "/", response_model=schemas.Tag, status_code=status.HTTP_201_CREATED
)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    """タグを作成"""
    try:
        # ビジネスロジックのバリデーション
        tag_service.validate_tag_data(tag)
        return tag_service.create_tag(db, tag)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=List[schemas.Tag])
def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """タグ一覧を取得"""
    return tag_service.get_tags(db, skip=skip, limit=limit)


@router.get("/{tag_id}", response_model=schemas.Tag)
def read_tag(tag_id: int, db: Session = Depends(get_db)):
    """タグを取得"""
    tag = tag_service.get_tag(db, tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return tag


@router.put("/{tag_id}", response_model=schemas.Tag)
def update_tag(
    tag_id: int, tag: schemas.TagUpdate, db: Session = Depends(get_db)
):
    """タグを更新"""
    updated_tag = tag_service.update_tag(db, tag_id, tag)
    if updated_tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return updated_tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """タグを削除"""
    success = tag_service.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
