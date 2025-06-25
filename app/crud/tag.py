"""
CRUD operations for Tag entity.

This module provides data access layer operations for the tag table.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from .. import models, schemas


class TagCRUD:
    """
    タグCRUDクラス

    タグエンティティの全てのデータアクセス操作を提供します。
    """

    def get(self, db: Session, id: int) -> Optional[models.Tag]:
        """IDでタグを取得"""
        return db.query(models.Tag).filter(models.Tag.id == id).first()

    def get_by_ssid(self, db: Session, ssid: str) -> Optional[models.Tag]:
        """SSIDでタグを取得"""
        return db.query(models.Tag).filter(models.Tag.ssid == ssid).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[models.Tag]:
        """タグ一覧を取得"""
        return db.query(models.Tag).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: schemas.TagCreate) -> models.Tag:
        """タグを作成"""
        db_tag = models.Tag(**obj_in.model_dump())
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag

    def update(self, db: Session, *, id: int, obj_in: schemas.TagUpdate) -> Optional[models.Tag]:
        """タグを更新"""
        db_tag = self.get(db, id)
        if db_tag:
            # 全フィールドを取得
            update_data = obj_in.model_dump()
            # None値を除外して更新対象フィールドのみを抽出
            filtered_data = {field: value for field, value in update_data.items() if value is not None}

            # 更新対象フィールドのみを設定
            for field, value in filtered_data.items():
                setattr(db_tag, field, value)

            db.commit()
            db.refresh(db_tag)
        return db_tag

    def remove(self, db: Session, *, id: int) -> bool:
        """タグを削除"""
        db_tag = self.get(db, id)
        if db_tag:
            db.delete(db_tag)
            db.commit()
            return True
        return False
