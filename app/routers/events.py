from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services import EventService

router = APIRouter(prefix="/events", tags=["events"])

# サービスインスタンス
event_service = EventService()


@router.post(
    "/",
    response_model=schemas.Event,
    status_code=status.HTTP_201_CREATED,
)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    """出来事を作成"""
    try:
        # ビジネスロジックのバリデーション
        event_service.validate_event_data(event)
        return event_service.create_event(db, event)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=List[schemas.Event])
def read_events(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """出来事一覧を取得"""
    return event_service.get_events(db, skip=skip, limit=limit)


@router.get("/{event_id}", response_model=schemas.Event)
def read_event(event_id: int, db: Session = Depends(get_db)):
    """出来事を取得"""
    event = event_service.get_event(db, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    return event


@router.put("/{event_id}", response_model=schemas.Event)
def update_event(
    event_id: int, event: schemas.EventUpdate, db: Session = Depends(get_db)
):
    """出来事を更新"""
    updated_event = event_service.update_event(db, event_id, event)
    if updated_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    return updated_event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """出来事を削除"""
    success = event_service.delete_event(db, event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
