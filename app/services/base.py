"""
ベースサービスクラス

すべてのサービスが継承する基底クラスです。
共通のビジネスロジックとエラーハンドリングを提供します。
"""

from typing import Any, Generic, List, Optional, TypeVar

from sqlalchemy.orm import Session

# ジェネリック型の定義
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    ベースサービスクラス

    すべてのサービスが継承する基底クラスです。
    共通のCRUD操作とビジネスロジックを提供します。
    """

    def __init__(self, crud_operations: Any):
        """
        初期化

        Args:
            crud_operations: CRUD操作オブジェクト
        """
        self.crud = crud_operations

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """IDでエンティティを取得"""
        return self.crud.get(db, id)

    def get_by_ssid(self, db: Session, ssid: str) -> Optional[ModelType]:
        """SSIDでエンティティを取得"""
        return self.crud.get_by_ssid(db, ssid)

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """エンティティ一覧を取得"""
        return self.crud.get_multi(db, skip=skip, limit=limit)

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """エンティティを作成"""
        return self.crud.create(db, obj_in=obj_in)

    def update(self, db: Session, *, id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """エンティティを更新"""
        return self.crud.update(db, id=id, obj_in=obj_in)

    def remove(self, db: Session, *, id: int) -> bool:
        """エンティティを削除"""
        return self.crud.remove(db, id=id)
