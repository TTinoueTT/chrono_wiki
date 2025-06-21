"""
CRUD operations for Event entity.

This module provides data access layer operations for the event table.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from .. import models, schemas


def create_event(db: Session, event: schemas.EventCreate) -> models.Event:
    """出来事を作成"""
    db_event = models.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


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
