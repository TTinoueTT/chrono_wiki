from typing import List, Optional

from sqlalchemy.orm import Session

from . import models, schemas


# Person CRUD operations
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


def create_person(db: Session, person: schemas.PersonCreate) -> models.Person:
    """人物を作成"""
    db_person = models.Person(**person.model_dump())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


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


# Tag CRUD operations
def get_tag(db: Session, tag_id: int) -> Optional[models.Tag]:
    """IDでタグを取得"""
    return db.query(models.Tag).filter(models.Tag.id == tag_id).first()


def get_tag_by_ssid(db: Session, ssid: str) -> Optional[models.Tag]:
    """SSIDでタグを取得"""
    return db.query(models.Tag).filter(models.Tag.ssid == ssid).first()


def get_tags(db: Session, skip: int = 0, limit: int = 100) -> List[models.Tag]:
    """タグ一覧を取得"""
    return db.query(models.Tag).offset(skip).limit(limit).all()


def create_tag(db: Session, tag: schemas.TagCreate) -> models.Tag:
    """タグを作成"""
    db_tag = models.Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


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


# Event CRUD operations
def get_event(db: Session, event_id: int) -> Optional[models.Event]:
    """IDで出来事を取得"""
    return db.query(models.Event).filter(models.Event.id == event_id).first()


def get_event_by_ssid(db: Session, ssid: str) -> Optional[models.Event]:
    """SSIDで出来事を取得"""
    return db.query(models.Event).filter(models.Event.ssid == ssid).first()


def get_events(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Event]:
    """出来事一覧を取得"""
    return db.query(models.Event).offset(skip).limit(limit).all()


def create_event(db: Session, event: schemas.EventCreate) -> models.Event:
    """出来事を作成"""
    db_event = models.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def update_event(
    db: Session, event_id: int, event: schemas.EventUpdate
) -> Optional[models.Event]:
    """出来事を更新"""
    db_event = get_event(db, event_id)
    if db_event:
        update_data = event.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_event, field, value)
        db.commit()
        db.refresh(db_event)
    return db_event


def delete_event(db: Session, event_id: int) -> bool:
    """出来事を削除"""
    db_event = get_event(db, event_id)
    if db_event:
        db.delete(db_event)
        db.commit()
        return True
    return False
