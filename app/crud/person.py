"""
CRUD operations for Person entity.

This module provides data access layer operations for the person table.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from .. import models, schemas


class PersonCRUD:
    """
    人物CRUDクラス

    人物エンティティの全てのデータアクセス操作を提供します。
    """

    def get(self, db: Session, id: int) -> Optional[models.Person]:
        """IDで人物を取得"""
        return db.query(models.Person).filter(models.Person.id == id).first()

    def get_by_ssid(self, db: Session, ssid: str) -> Optional[models.Person]:
        """SSIDで人物を取得"""
        return db.query(models.Person).filter(models.Person.ssid == ssid).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[models.Person]:
        """人物一覧を取得"""
        return db.query(models.Person).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: schemas.PersonCreate) -> models.Person:
        """人物を作成"""
        db_person = models.Person(**obj_in.model_dump())
        db.add(db_person)
        db.commit()
        db.refresh(db_person)
        return db_person

    def update(self, db: Session, *, id: int, obj_in: schemas.PersonUpdate) -> Optional[models.Person]:
        """人物を更新"""
        db_person = self.get(db, id)
        if db_person:
            # 全フィールドを取得
            update_data = obj_in.model_dump()
            # None値を除外して更新対象フィールドのみを抽出
            filtered_data = {field: value for field, value in update_data.items() if value is not None}

            # 更新対象フィールドのみを設定
            for field, value in filtered_data.items():
                setattr(db_person, field, value)

            db.commit()
            db.refresh(db_person)
        return db_person

    def remove(self, db: Session, *, id: int) -> bool:
        """人物を削除"""
        db_person = self.get(db, id)
        if db_person:
            db.delete(db_person)
            db.commit()
            return True
        return False
