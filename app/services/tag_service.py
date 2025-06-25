"""
タグサービス

タグエンティティのビジネスロジックを実装します。
シンプルなDI（依存性注入）パターンを使用してCRUD層との結合度を下げます。
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from .. import schemas
from ..crud.tag import TagCRUD
from .base import BaseService


class TagService(BaseService[schemas.Tag, schemas.TagCreate, schemas.TagUpdate]):
    """
    タグサービス

    タグエンティティのビジネスロジックを実装します。
    シンプルなDI（依存性注入）パターンを使用してCRUD層との結合度を下げます。
    """

    def __init__(self, tag_crud=None):
        """
        初期化

        Args:
            tag_crud: タグCRUDオブジェクト（デフォルトでTagCRUD()を使用）
        """
        if tag_crud is None:
            tag_crud = TagCRUD()
        super().__init__(tag_crud)

    def create_tag(self, db: Session, tag: schemas.TagCreate) -> schemas.Tag:
        """
        タグを作成

        Args:
            db: データベースセッション
            tag: タグ作成データ

        Returns:
            作成されたタグ

        Raises:
            ValueError: SSIDが既に存在する場合、またはバリデーションエラーの場合
        """
        # ビジネスルール: データバリデーション
        self.validate_tag_data(tag)

        # ビジネスルール: SSIDの重複チェック
        existing_tag = self.get_by_ssid(db, tag.ssid)
        if existing_tag:
            raise ValueError(f"SSID '{tag.ssid}' is already registered")

        # CRUD操作を実行
        created_tag = self.create(db, obj_in=tag)

        # レスポンススキーマに変換
        return schemas.Tag.model_validate(created_tag)

    def get_tag(self, db: Session, tag_id: int) -> Optional[schemas.Tag]:
        """
        タグを取得

        Args:
            db: データベースセッション
            tag_id: タグID

        Returns:
            タグまたはNone
        """
        tag = self.get(db, tag_id)
        if tag:
            return schemas.Tag.model_validate(tag)
        return None

    def get_tag_by_ssid(self, db: Session, ssid: str) -> Optional[schemas.Tag]:
        """
        SSIDでタグを取得

        Args:
            db: データベースセッション
            ssid: タグのSSID

        Returns:
            タグまたはNone
        """
        tag = self.get_by_ssid(db, ssid)
        if tag:
            return schemas.Tag.model_validate(tag)
        return None

    def get_tags(self, db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Tag]:
        """
        タグ一覧を取得

        Args:
            db: データベースセッション
            skip: スキップ数
            limit: 取得上限数

        Returns:
            タグのリスト
        """
        tags = self.get_multi(db, skip=skip, limit=limit)
        return [schemas.Tag.model_validate(t) for t in tags]

    def update_tag(self, db: Session, tag_id: int, tag: schemas.TagUpdate) -> Optional[schemas.Tag]:
        """
        タグを更新

        Args:
            db: データベースセッション
            tag_id: タグID
            tag: 更新データ

        Returns:
            更新されたタグまたはNone

        Raises:
            ValueError: バリデーションエラーの場合
        """
        # ビジネスルール: 更新データのバリデーション
        self.validate_tag_update_data(tag)

        # CRUD操作を実行
        updated_tag = self.update(db, id=tag_id, obj_in=tag)

        if updated_tag:
            return schemas.Tag.model_validate(updated_tag)
        return None

    def delete_tag(self, db: Session, tag_id: int) -> bool:
        """
        タグを削除

        Args:
            db: データベースセッション
            tag_id: タグID

        Returns:
            削除成功フラグ
        """
        return self.remove(db, id=tag_id)

    def validate_tag_data(self, tag: schemas.TagCreate) -> None:
        """
        タグデータのバリデーション

        Args:
            tag: タグデータ

        Raises:
            ValueError: バリデーションエラーの場合
        """
        # ビジネスルール: タグ名は必須
        if not tag.name or not tag.name.strip():
            raise ValueError("Tag name is required")

        # ビジネスルール: SSIDは必須
        if not tag.ssid or not tag.ssid.strip():
            raise ValueError("SSID is required")

        # ビジネスルール: タグ名の長さ制限
        if len(tag.name) > 50:
            raise ValueError("Tag name must be 50 characters or less")

    def validate_tag_update_data(self, tag: schemas.TagUpdate) -> None:
        """
        タグ更新データのバリデーション

        Args:
            tag: タグ更新データ

        Raises:
            ValueError: バリデーションエラーの場合
        """
        # ビジネスルール: タグ名の長さ制限（指定されている場合）
        if tag.name and len(tag.name) > 50:
            raise ValueError("Tag name must be 50 characters or less")
