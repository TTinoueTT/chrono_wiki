"""
イベントサービス

イベントエンティティのビジネスロジックを実装します。
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from .. import schemas
from ..crud import event as crud
from .base import BaseService


class EventService(BaseService):
    """
    イベントサービス

    イベントエンティティのビジネスロジックを実装します。
    """

    def __init__(self):
        """初期化"""
        super().__init__(crud)

    def create_event(
        self, db: Session, event: schemas.EventCreate
    ) -> schemas.Event:
        """
        イベントを作成

        Args:
            db: データベースセッション
            event: イベント作成データ

        Returns:
            作成されたイベント

        Raises:
            ValueError: SSIDが既に存在する場合
        """
        # ビジネスルール: SSIDの重複チェック
        existing_event = self.get_by_ssid(db, event.ssid)
        if existing_event:
            raise ValueError(f"SSID '{event.ssid}' is already registered")

        return self.create(db, obj_in=event)

    def get_event(self, db: Session, event_id: int) -> Optional[schemas.Event]:
        """
        イベントを取得

        Args:
            db: データベースセッション
            event_id: イベントID

        Returns:
            イベントまたはNone
        """
        return self.get(db, event_id)

    def get_event_by_ssid(
        self, db: Session, ssid: str
    ) -> Optional[schemas.Event]:
        """
        SSIDでイベントを取得

        Args:
            db: データベースセッション
            ssid: イベントのSSID

        Returns:
            イベントまたはNone
        """
        return self.get_by_ssid(db, ssid)

    def get_events(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[schemas.Event]:
        """
        イベント一覧を取得

        Args:
            db: データベースセッション
            skip: スキップ数
            limit: 取得上限数

        Returns:
            イベントのリスト
        """
        return self.get_multi(db, skip=skip, limit=limit)

    def update_event(
        self, db: Session, event_id: int, event: schemas.EventUpdate
    ) -> Optional[schemas.Event]:
        """
        イベントを更新

        Args:
            db: データベースセッション
            event_id: イベントID
            event: 更新データ

        Returns:
            更新されたイベントまたはNone
        """
        return self.update(db, id=event_id, obj_in=event)

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
