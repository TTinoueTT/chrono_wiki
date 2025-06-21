"""
CRUD operations for Tag entity.

This module provides data access layer operations for the tag table.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from .. import models, schemas


def create_tag(db: Session, tag: schemas.TagCreate) -> models.Tag:
    """タグを作成"""
    db_tag = models.Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def get_tag(db: Session, tag_id: int) -> Optional[models.Tag]:
    """IDでタグを取得"""
    return db.query(models.Tag).filter(models.Tag.id == tag_id).first()


def get_tag_by_ssid(db: Session, ssid: str) -> Optional[models.Tag]:
    """SSIDでタグを取得"""
    return db.query(models.Tag).filter(models.Tag.ssid == ssid).first()


def get_tags(db: Session, skip: int = 0, limit: int = 100) -> List[models.Tag]:
    """タグ一覧を取得"""
    return db.query(models.Tag).offset(skip).limit(limit).all()


def update_tag(
    db: Session, tag_id: int, tag: schemas.TagUpdate
) -> Optional[models.Tag]:
    """タグを更新"""
    db_tag = get_tag(db, tag_id)
    if db_tag:
        update_data = tag.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tag, field, value)
        db.commit()
        db.refresh(db_tag)
    return db_tag


def delete_tag(db: Session, tag_id: int) -> bool:
    """タグを削除"""
    db_tag = get_tag(db, tag_id)
    if db_tag:
        db.delete(db_tag)
        db.commit()
        return True
    return False
