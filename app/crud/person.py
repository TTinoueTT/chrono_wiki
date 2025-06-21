"""
CRUD operations for Person entity.

This module provides data access layer operations for the person table.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from .. import models, schemas


def create_person(db: Session, person: schemas.PersonCreate) -> models.Person:
    """人物を作成"""
    db_person = models.Person(**person.model_dump())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


def get_person(db: Session, person_id: int) -> Optional[models.Person]:
    """IDで人物を取得"""
    return (
        db.query(models.Person).filter(models.Person.id == person_id).first()
    )


def get_person_by_ssid(db: Session, ssid: str) -> Optional[models.Person]:
    """SSIDで人物を取得"""
    return db.query(models.Person).filter(models.Person.ssid == ssid).first()


def get_persons(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Person]:
    """人物一覧を取得"""
    return db.query(models.Person).offset(skip).limit(limit).all()


def update_person(
    db: Session, person_id: int, person: schemas.PersonUpdate
) -> Optional[models.Person]:
    """人物を更新"""
    db_person = get_person(db, person_id)
    if db_person:
        update_data = person.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_person, field, value)
        db.commit()
        db.refresh(db_person)
    return db_person


def delete_person(db: Session, person_id: int) -> bool:
    """人物を削除"""
    db_person = get_person(db, person_id)
    if db_person:
        db.delete(db_person)
        db.commit()
        return True
    return False
