"""
バッチ処理ルーター

APIキー認証専用のバッチ処理エンドポイントを提供します。
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..dependencies.api_key_auth import verify_token
from ..services import EventService, PersonService, TagService

router = APIRouter(tags=["batch"])


def get_person_service() -> PersonService:
    """人物サービスのインスタンスを取得"""
    return PersonService()


def get_event_service() -> EventService:
    """イベントサービスのインスタンスを取得"""
    return EventService()


def get_tag_service() -> TagService:
    """タグサービスのインスタンスを取得"""
    return TagService()


@router.get("/batch/persons/", response_model=List[schemas.Person])
def batch_get_persons(
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db),
    person_service: PersonService = Depends(get_person_service),
    api_key=Depends(verify_token),
):
    """
    人物一覧をバッチ取得（APIキー認証専用）

    Args:
        skip: スキップ数
        limit: 取得上限数（最大1000）
        db: データベースセッション
        person_service: 人物サービス
        api_key: APIキー（認証用）

    Returns:
        人物のリスト
    """
    # バッチ処理用の制限
    if limit > 1000:
        limit = 1000

    return person_service.get_persons(db, skip=skip, limit=limit)


@router.get("/batch/events/", response_model=List[schemas.Event])
def batch_get_events(
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db),
    event_service: EventService = Depends(get_event_service),
    api_key=Depends(verify_token),
):
    """
    イベント一覧をバッチ取得（APIキー認証専用）

    Args:
        skip: スキップ数
        limit: 取得上限数（最大1000）
        db: データベースセッション
        event_service: イベントサービス
        api_key: APIキー（認証用）

    Returns:
        イベントのリスト
    """
    # バッチ処理用の制限
    if limit > 1000:
        limit = 1000

    return event_service.get_events(db, skip=skip, limit=limit)


@router.get("/batch/tags/", response_model=List[schemas.Tag])
def batch_get_tags(
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db),
    tag_service: TagService = Depends(get_tag_service),
    api_key=Depends(verify_token),
):
    """
    タグ一覧をバッチ取得（APIキー認証専用）

    Args:
        skip: スキップ数
        limit: 取得上限数（最大1000）
        db: データベースセッション
        tag_service: タグサービス
        api_key: APIキー（認証用）

    Returns:
        タグのリスト
    """
    # バッチ処理用の制限
    if limit > 1000:
        limit = 1000

    return tag_service.get_tags(db, skip=skip, limit=limit)


@router.post("/batch/persons/", response_model=List[schemas.Person])
def batch_create_persons(
    persons: List[schemas.PersonCreate],
    db: Session = Depends(get_db),
    person_service: PersonService = Depends(get_person_service),
    api_key=Depends(verify_token),
):
    """
    人物をバッチ作成（APIキー認証専用）

    Args:
        persons: 人物作成データのリスト
        db: データベースセッション
        person_service: 人物サービス
        api_key: APIキー（認証用）

    Returns:
        作成された人物のリスト

    Raises:
        HTTPException: バリデーションエラーの場合
    """
    if len(persons) > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Batch size cannot exceed 100 items")

    created_persons = []
    for person in persons:
        try:
            created_person = person_service.create_person(db, person)
            created_persons.append(created_person)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating person: {str(e)}")

    return created_persons


@router.post("/batch/events/", response_model=List[schemas.Event])
def batch_create_events(
    events: List[schemas.EventCreate],
    db: Session = Depends(get_db),
    event_service: EventService = Depends(get_event_service),
    api_key=Depends(verify_token),
):
    """
    イベントをバッチ作成（APIキー認証専用）

    Args:
        events: イベント作成データのリスト
        db: データベースセッション
        event_service: イベントサービス
        api_key: APIキー（認証用）

    Returns:
        作成されたイベントのリスト

    Raises:
        HTTPException: バリデーションエラーの場合
    """
    if len(events) > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Batch size cannot exceed 100 items")

    created_events = []
    for event in events:
        try:
            created_event = event_service.create_event(db, event)
            created_events.append(created_event)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating event: {str(e)}")

    return created_events


@router.get("/batch/stats")
def get_batch_stats(
    db: Session = Depends(get_db),
    person_service: PersonService = Depends(get_person_service),
    event_service: EventService = Depends(get_event_service),
    tag_service: TagService = Depends(get_tag_service),
    api_key=Depends(verify_token),
):
    """
    バッチ処理用統計情報を取得（APIキー認証専用）

    Args:
        db: データベースセッション
        person_service: 人物サービス
        event_service: イベントサービス
        tag_service: タグサービス
        api_key: APIキー（認証用）

    Returns:
        統計情報
    """
    # 各サービスの統計情報を取得
    persons = person_service.get_persons(db, skip=0, limit=1)
    events = event_service.get_events(db, skip=0, limit=1)
    tags = tag_service.get_tags(db, skip=0, limit=1)

    # 実際のカウントは別途実装が必要
    return {
        "persons": len(persons),
        "events": len(events),
        "tags": len(tags),
        "total": len(persons) + len(events) + len(tags),
    }
