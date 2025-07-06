from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services import EventService

router = APIRouter(tags=["events"])


def get_event_service() -> EventService:
    """
    イベントサービスのインスタンスを取得

    Returns:
        EventService: イベントサービスのインスタンス
    """
    return EventService()


@router.post(
    "/events/",
    response_model=schemas.Event,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db),
    event_service: EventService = Depends(get_event_service),
):
    """
    イベントを作成

    Args:
        event: イベント作成データ
        db: データベースセッション
        event_service: イベントサービス（DI）

    Returns:
        作成されたイベント

    Raises:
        HTTPException: バリデーションエラーまたは重複エラーの場合
    """
    try:
        return event_service.create_event(db, event)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/events/", response_model=List[schemas.Event])
def read_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    event_service: EventService = Depends(get_event_service),
):
    """
    イベント一覧を取得

    Args:
        skip: スキップ数
        limit: 取得上限数
        db: データベースセッション
        event_service: イベントサービス（DI）

    Returns:
        イベントのリスト
    """
    return event_service.get_events(db, skip=skip, limit=limit)


@router.get("/events/{event_id}", response_model=schemas.Event)
def read_event(
    event_id: int,
    db: Session = Depends(get_db),
    event_service: EventService = Depends(get_event_service),
):
    """
    イベントを取得

    Args:
        event_id: イベントID
        db: データベースセッション
        event_service: イベントサービス（DI）

    Returns:
        イベントデータ

    Raises:
        HTTPException: イベントが見つからない場合
    """
    event = event_service.get_event(db, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return event


@router.put("/events/{event_id}", response_model=schemas.Event)
def update_event(
    event_id: int,
    event: schemas.EventUpdate,
    db: Session = Depends(get_db),
    event_service: EventService = Depends(get_event_service),
):
    """
    イベントを更新

    Args:
        event_id: イベントID
        event: 更新データ
        db: データベースセッション
        event_service: イベントサービス（DI）

    Returns:
        更新されたイベントデータ

    Raises:
        HTTPException: イベントが見つからない場合またはバリデーションエラーの場合
    """
    try:
        updated_event = event_service.update_event(db, event_id, event)
        if updated_event is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )
        return updated_event
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    event_service: EventService = Depends(get_event_service),
):
    """
    イベントを削除

    Args:
        event_id: イベントID
        db: データベースセッション
        event_service: イベントサービス（DI）

    Raises:
        HTTPException: イベントが見つからない場合
    """
    success = event_service.delete_event(db, event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
