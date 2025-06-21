"""
ベースサービスクラス

すべてのサービスが継承する基底クラスです。
共通のビジネスロジックとエラーハンドリングを提供します。
"""

from typing import Generic, List, Optional, TypeVar

from sqlalchemy.orm import Session

from .. import schemas

# ジェネリック型の定義
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=schemas.BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=schemas.BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    ベースサービスクラス

    すべてのサービスが継承する基底クラスです。
    共通のCRUD操作とビジネスロジックを提供します。
    """

    def __init__(self, crud_module):
        """
        初期化

        Args:
            crud_module: CRUDモジュール（event, person, tag）
        """
        self.crud = crud_module

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        IDでエンティティを取得

        Args:
            db: データベースセッション
            id: エンティティID

        Returns:
            エンティティまたはNone
        """
        return (
            self.crud.get_event(db, id)
            if hasattr(self.crud, "get_event")
            else (
                self.crud.get_person(db, id)
                if hasattr(self.crud, "get_person")
                else self.crud.get_tag(db, id)
            )
        )

    def get_by_ssid(self, db: Session, ssid: str) -> Optional[ModelType]:
        """
        SSIDでエンティティを取得

        Args:
            db: データベースセッション
            ssid: エンティティのSSID

        Returns:
            エンティティまたはNone
        """
        return (
            self.crud.get_event_by_ssid(db, ssid)
            if hasattr(self.crud, "get_event_by_ssid")
            else (
                self.crud.get_person_by_ssid(db, ssid)
                if hasattr(self.crud, "get_person_by_ssid")
                else self.crud.get_tag_by_ssid(db, ssid)
            )
        )

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        エンティティ一覧を取得

        Args:
            db: データベースセッション
            skip: スキップ数
            limit: 取得上限数

        Returns:
            エンティティのリスト
        """
        return (
            self.crud.get_events(db, skip=skip, limit=limit)
            if hasattr(self.crud, "get_events")
            else (
                self.crud.get_persons(db, skip=skip, limit=limit)
                if hasattr(self.crud, "get_persons")
                else self.crud.get_tags(db, skip=skip, limit=limit)
            )
        )

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        エンティティを作成

        Args:
            db: データベースセッション
            obj_in: 作成データ

        Returns:
            作成されたエンティティ
        """
        return (
            self.crud.create_event(db, obj_in)
            if hasattr(self.crud, "create_event")
            else (
                self.crud.create_person(db, obj_in)
                if hasattr(self.crud, "create_person")
                else self.crud.create_tag(db, obj_in)
            )
        )

    def update(
        self, db: Session, *, id: int, obj_in: UpdateSchemaType
    ) -> Optional[ModelType]:
        """
        エンティティを更新

        Args:
            db: データベースセッション
            id: 更新対象のエンティティID
            obj_in: 更新データ

        Returns:
            更新されたエンティティまたはNone
        """
        return (
            self.crud.update_event(db, id, obj_in)
            if hasattr(self.crud, "update_event")
            else (
                self.crud.update_person(db, id, obj_in)
                if hasattr(self.crud, "update_person")
                else self.crud.update_tag(db, id, obj_in)
            )
        )

    def remove(self, db: Session, *, id: int) -> bool:
        """
        エンティティを削除

        Args:
            db: データベースセッション
            id: 削除対象のエンティティID

        Returns:
            削除成功フラグ
        """
        return (
            self.crud.delete_event(db, id)
            if hasattr(self.crud, "delete_event")
            else (
                self.crud.delete_person(db, id)
                if hasattr(self.crud, "delete_person")
                else self.crud.delete_tag(db, id)
            )
        )
