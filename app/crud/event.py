"""
CRUD operations for Event entity.

This module provides data access layer operations for the event table.
"""

from datetime import date
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas


class EventCRUD:
    """
    イベントCRUDクラス

    イベントエンティティの全てのデータアクセス操作を提供します。
    """

    def get(self, db: Session, id: int) -> Optional[models.Event]:
        """IDでイベントを取得"""
        return db.query(models.Event).filter(models.Event.id == id).first()

    def get_by_ssid(self, db: Session, ssid: str) -> Optional[models.Event]:
        """SSIDでイベントを取得"""
        return db.query(models.Event).filter(models.Event.ssid == ssid).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[models.Event]:
        """イベント一覧を取得"""
        return db.query(models.Event).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: schemas.EventCreate) -> models.Event:
        """イベントを作成"""
        db_event = models.Event(**obj_in.model_dump())
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event

    def update(self, db: Session, *, id: int, obj_in: schemas.EventUpdate) -> Optional[models.Event]:
        """イベントを更新"""
        db_event = self.get(db, id)
        if db_event:
            # 全フィールドを取得
            update_data = obj_in.model_dump()
            # None値を除外して更新対象フィールドのみを抽出
            filtered_data = {field: value for field, value in update_data.items() if value is not None}

            # 更新対象フィールドのみを設定
            for field, value in filtered_data.items():
                setattr(db_event, field, value)

            db.commit()
            db.refresh(db_event)
        return db_event

    def remove(self, db: Session, *, id: int) -> bool:
        """イベントを削除"""
        db_event = self.get(db, id)
        if db_event:
            db.delete(db_event)
            db.commit()
            return True
        return False

    # 拡張DBアクセス関数
    def get_events_by_date_range(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        skip: int = 0,
        limit: int = 100,
    ) -> List[models.Event]:
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
        """
        return (
            db.query(models.Event)
            .filter(
                models.Event.start_date >= start_date,
                models.Event.start_date <= end_date,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_events_by_title_search(
        self, db: Session, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[models.Event]:
        """
        タイトルでイベントを検索

        Args:
            db: データベースセッション
            search_term: 検索語
            skip: スキップ数
            limit: 取得上限数

        Returns:
            イベントのリスト
        """
        return (
            db.query(models.Event).filter(models.Event.title.ilike(f"%{search_term}%")).offset(skip).limit(limit).all()
        )

    def get_events_by_location(
        self, db: Session, location_name: str, skip: int = 0, limit: int = 100
    ) -> List[models.Event]:
        """
        場所でイベントを検索

        Args:
            db: データベースセッション
            location_name: 場所名
            skip: スキップ数
            limit: 取得上限数

        Returns:
            イベントのリスト
        """
        return (
            db.query(models.Event)
            .filter(models.Event.location_name.ilike(f"%{location_name}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_events_by_year(self, db: Session, year: int) -> int:
        """
        指定年のイベント数を取得

        Args:
            db: データベースセッション
            year: 年

        Returns:
            イベント数
        """
        return (
            db.query(models.Event)
            .filter(
                models.Event.start_date >= date(year, 1, 1),
                models.Event.start_date <= date(year, 12, 31),
            )
            .count()
        )

    def get_events_by_person(self, db: Session, person_id: int, skip: int = 0, limit: int = 100) -> List[models.Event]:
        """
        人物に関連するイベントを取得

        Args:
            db: データベースセッション
            person_id: 人物ID
            skip: スキップ数
            limit: 取得上限数

        Returns:
            イベントのリスト
        """
        # 将来的に人物-イベントの関連テーブルが追加された場合の実装
        # 現在は基本的な実装
        return (
            db.query(models.Event)
            .filter(models.Event.description.ilike(f"%{person_id}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_events_by_tag(self, db: Session, tag_id: int, skip: int = 0, limit: int = 100) -> List[models.Event]:
        """
        タグに関連するイベントを取得

        Args:
            db: データベースセッション
            tag_id: タグID
            skip: スキップ数
            limit: 取得上限数

        Returns:
            イベントのリスト
        """
        # 将来的にイベント-タグの関連テーブルが追加された場合の実装
        # 現在は基本的な実装
        return (
            db.query(models.Event).filter(models.Event.description.ilike(f"%{tag_id}%")).offset(skip).limit(limit).all()
        )

    def get_events_statistics(self, db: Session) -> dict:
        """
        イベントの統計情報を取得

        Args:
            db: データベースセッション

        Returns:
            統計情報の辞書
        """
        total_events = db.query(models.Event).count()

        # 年別統計
        yearly_stats = (
            db.query(
                func.extract("year", models.Event.start_date).label("year"),
                func.count(models.Event.id).label("count"),
            )
            .group_by("year")
            .all()
        )

        return {
            "total_events": total_events,
            "yearly_statistics": [{"year": int(stat.year), "count": stat.count} for stat in yearly_stats],
        }
