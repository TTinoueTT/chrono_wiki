from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..crud import tag as crud
from ..database import get_db

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post(
    "/", response_model=schemas.Tag, status_code=status.HTTP_201_CREATED
)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    """タグを作成"""
    db_tag = crud.get_tag_by_ssid(db, ssid=tag.ssid)
    if db_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SSID already registered",
        )
    return crud.create_tag(db=db, tag=tag)


@router.get("/", response_model=List[schemas.Tag])
def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """タグ一覧を取得"""
    tags = crud.get_tags(db, skip=skip, limit=limit)
    return tags


@router.get("/{tag_id}", response_model=schemas.Tag)
def read_tag(tag_id: int, db: Session = Depends(get_db)):
    """タグを取得"""
    db_tag = crud.get_tag(db, tag_id=tag_id)
    if db_tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return db_tag


@router.put("/{tag_id}", response_model=schemas.Tag)
def update_tag(
    tag_id: int, tag: schemas.TagUpdate, db: Session = Depends(get_db)
):
    """タグを更新"""
    db_tag = crud.update_tag(db, tag_id=tag_id, tag=tag)
    if db_tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return db_tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """タグを削除"""
    success = crud.delete_tag(db, tag_id=tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
