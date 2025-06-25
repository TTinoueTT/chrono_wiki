"""
イベントサービス

イベントエンティティのビジネスロジックを実装します。
シンプルなDI（依存性注入）パターンを使用してCRUD層との結合度を下げます。
"""

from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from .. import schemas
from ..crud.event import EventCRUD
from .base import BaseService


class EventService(BaseService[schemas.Event, schemas.EventCreate, schemas.EventUpdate]):
    """
    イベントサービス

    イベントエンティティのビジネスロジックを実装します。
    シンプルなDI（依存性注入）パターンを使用してCRUD層との結合度を下げます。
    """

    def __init__(self, event_crud=None):
        """
        初期化

        Args:
            event_crud: イベントCRUDオブジェクト（デフォルトでEventCRUD()を使用）
        """
        if event_crud is None:
            event_crud = EventCRUD()
        super().__init__(event_crud)

    def create_event(self, db: Session, event: schemas.EventCreate) -> schemas.Event:
        """
        イベントを作成

        Args:
            db: データベースセッション
            event: イベント作成データ

        Returns:
            作成されたイベント

        Raises:
            ValueError: SSIDが既に存在する場合、またはバリデーションエラーの場合
        """
        # ビジネスルール: データバリデーション
        self.validate_event_data(event)

        # ビジネスルール: SSIDの重複チェック
        existing_event = self.get_by_ssid(db, event.ssid)
        if existing_event:
            raise ValueError(f"SSID '{event.ssid}' is already registered")

        # CRUD操作を実行
        created_event = self.create(db, obj_in=event)

        # レスポンススキーマに変換
        return schemas.Event.model_validate(created_event)

    def get_event(self, db: Session, event_id: int) -> Optional[schemas.Event]:
        """
        イベントを取得

        Args:
            db: データベースセッション
            event_id: イベントID

        Returns:
            イベントまたはNone
        """
        event = self.get(db, event_id)
        if event:
            return schemas.Event.model_validate(event)
        return None

    def get_event_by_ssid(self, db: Session, ssid: str) -> Optional[schemas.Event]:
        """
        SSIDでイベントを取得

        Args:
            db: データベースセッション
            ssid: イベントのSSID

        Returns:
            イベントまたはNone
        """
        event = self.get_by_ssid(db, ssid)
        if event:
            return schemas.Event.model_validate(event)
        return None

    def get_events(self, db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Event]:
        """
        イベント一覧を取得

        Args:
            db: データベースセッション
            skip: スキップ数
            limit: 取得上限数

        Returns:
            イベントのリスト
        """
        events = self.get_multi(db, skip=skip, limit=limit)
        return [schemas.Event.model_validate(e) for e in events]

    def update_event(self, db: Session, event_id: int, event: schemas.EventUpdate) -> Optional[schemas.Event]:
        """
        イベントを更新

        Args:
            db: データベースセッション
            event_id: イベントID
            event: 更新データ

        Returns:
            更新されたイベントまたはNone

        Raises:
            ValueError: バリデーションエラーの場合
        """
        # ビジネスルール: 更新データのバリデーション
        self.validate_event_update_data(event)

        # CRUD操作を実行
        updated_event = self.update(db, id=event_id, obj_in=event)

        if updated_event:
            return schemas.Event.model_validate(updated_event)
        return None

    def delete_event(self, db: Session, event_id: int) -> bool:
        """
        イベントを削除

        Args:
            db: データベースセッション
            event_id: イベントID

        Returns:
            削除成功フラグ
        """
        return self.remove(db, id=event_id)

    def validate_event_data(self, event: schemas.EventCreate) -> None:
        """
        イベントデータのバリデーション

        Args:
            event: イベントデータ

        Raises:
            ValueError: バリデーションエラーの場合
        """
        # ビジネスルール: タイトルは必須
        if not event.title or not event.title.strip():
            raise ValueError("Title is required")

        # ビジネスルール: SSIDは必須
        if not event.ssid or not event.ssid.strip():
            raise ValueError("SSID is required")

        # ビジネスルール: 日付の整合性チェック
        if event.start_date and event.end_date:
            if event.start_date > event.end_date:
                raise ValueError("Start date cannot be after end date")

    def validate_event_update_data(self, event: schemas.EventUpdate) -> None:
        """
        イベント更新データのバリデーション

        Args:
            event: イベント更新データ

        Raises:
            ValueError: バリデーションエラーの場合
        """
        # ビジネスルール: 日付の整合性チェック（両方が指定されている場合）
        if event.start_date and event.end_date:
            if event.start_date > event.end_date:
                raise ValueError("Start date cannot be after end date")

    def get_events_by_date_range(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        skip: int = 0,
        limit: int = 100,
    ) -> List[schemas.Event]:
        """
        日付範囲でイベントを取得

        Args:
            db: データベースセッション
            start_date: 開始日
            end_date: 終了日
            skip: スキップ数
            limit: 取得上限数

        Returns:
            イベントのリスト

        Raises:
            ValueError: 日付範囲が無効な場合
        """
        # ビジネスルール: 日付範囲の検証
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")

        # CRUD層の関数を直接呼び出し
        event_crud = EventCRUD()
        events = event_crud.get_events_by_date_range(db, start_date, end_date, skip=skip, limit=limit)

        # ビジネスロジック: Pydanticスキーマに変換
        return [schemas.Event.model_validate(event) for event in events]

    def search_events_by_title(
        self, db: Session, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[schemas.Event]:
        """
        タイトルでイベントを検索

        Args:
            db: データベースセッション
            search_term: 検索語
            skip: スキップ数
            limit: 取得上限数

        Returns:
            イベントのリスト

        Raises:
            ValueError: 検索語が無効な場合
        """
        # ビジネスルール: 検索語の検証
        if not search_term or not search_term.strip():
            raise ValueError("Search term is required")

        # CRUD層の関数を直接呼び出し
        event_crud = EventCRUD()
        events = event_crud.get_events_by_title_search(db, search_term, skip=skip, limit=limit)

        # ビジネスロジック: Pydanticスキーマに変換
        return [schemas.Event.model_validate(event) for event in events]

    def get_events_by_location(
        self, db: Session, location_name: str, skip: int = 0, limit: int = 100
    ) -> List[schemas.Event]:
        """
        場所でイベントを検索

        Args:
            db: データベースセッション
            location_name: 場所名
            skip: スキップ数
            limit: 取得上限数

        Returns:
            イベントのリスト

        Raises:
            ValueError: 場所名が無効な場合
        """
        # ビジネスルール: 場所名の検証
        if not location_name or not location_name.strip():
            raise ValueError("Location name is required")

        # CRUD層の関数を直接呼び出し
        event_crud = EventCRUD()
        events = event_crud.get_events_by_location(db, location_name, skip=skip, limit=limit)

        # ビジネスロジック: Pydanticスキーマに変換
        return [schemas.Event.model_validate(event) for event in events]

    def get_event_statistics_by_year(self, db: Session, year: int) -> dict:
        """
        指定年のイベント統計を取得

        Args:
            db: データベースセッション
            year: 年

        Returns:
            統計情報の辞書

        Raises:
            ValueError: 年が無効な場合
        """
        # ビジネスルール: 年の検証
        if year < 1 or year > 9999:
            raise ValueError("Year must be between 1 and 9999")

        # CRUD層の関数を直接呼び出し
        event_crud = EventCRUD()
        event_count = event_crud.count_events_by_year(db, year)

        # ビジネスロジック: 統計情報の構築
        return {
            "year": year,
            "total_events": event_count,
            "average_events_per_month": (event_count / 12 if event_count > 0 else 0),
        }
