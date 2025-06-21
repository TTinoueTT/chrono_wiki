from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/events", tags=["events"])


@router.post(
    "/",
    response_model=schemas.Event,
    status_code=status.HTTP_201_CREATED,
)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    """出来事を作成"""
    db_event = crud.get_event_by_ssid(db, ssid=event.ssid)
    if db_event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SSID already registered",
        )
    return crud.create_event(db=db, event=event)


@router.get("/", response_model=List[schemas.Event])
def read_events(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """出来事一覧を取得"""
    events = crud.get_events(db, skip=skip, limit=limit)
    return events


@router.get("/{event_id}", response_model=schemas.Event)
def read_event(event_id: int, db: Session = Depends(get_db)):
    """出来事を取得"""
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    return db_event


@router.put("/{event_id}", response_model=schemas.Event)
def update_event(
    event_id: int, event: schemas.EventUpdate, db: Session = Depends(get_db)
):
    """出来事を更新"""
    db_event = crud.update_event(db, event_id=event_id, event=event)
    if db_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    return db_event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """出来事を削除"""
    success = crud.delete_event(db, event_id=event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
