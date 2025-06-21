"""
タグサービス

タグエンティティのビジネスロジックを実装します。
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from .. import schemas
from ..crud import tag as crud
from .base import BaseService


class TagService(BaseService):
    """
    タグサービス

    タグエンティティのビジネスロジックを実装します。
    """

    def __init__(self):
        """初期化"""
        super().__init__(crud)

    def create_tag(self, db: Session, tag: schemas.TagCreate) -> schemas.Tag:
        """
        タグを作成

        Args:
            db: データベースセッション
            tag: タグ作成データ

        Returns:
            作成されたタグ

        Raises:
            ValueError: SSIDが既に存在する場合
        """
        # ビジネスルール: SSIDの重複チェック
        existing_tag = self.get_by_ssid(db, tag.ssid)
        if existing_tag:
            raise ValueError(f"SSID '{tag.ssid}' is already registered")

        return self.create(db, obj_in=tag)

    def get_tag(self, db: Session, tag_id: int) -> Optional[schemas.Tag]:
        """
        タグを取得

        Args:
            db: データベースセッション
            tag_id: タグID

        Returns:
            タグまたはNone
        """
        return self.get(db, tag_id)

    def get_tag_by_ssid(self, db: Session, ssid: str) -> Optional[schemas.Tag]:
        """
        SSIDでタグを取得

        Args:
            db: データベースセッション
            ssid: タグのSSID

        Returns:
            タグまたはNone
        """
        return self.get_by_ssid(db, ssid)

    def get_tags(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[schemas.Tag]:
        """
        タグ一覧を取得

        Args:
            db: データベースセッション
            skip: スキップ数
            limit: 取得上限数

        Returns:
            タグのリスト
        """
        return self.get_multi(db, skip=skip, limit=limit)

    def update_tag(
        self, db: Session, tag_id: int, tag: schemas.TagUpdate
    ) -> Optional[schemas.Tag]:
        """
        タグを更新

        Args:
            db: データベースセッション
            tag_id: タグID
            tag: 更新データ

        Returns:
            更新されたタグまたはNone
        """
        return self.update(db, id=tag_id, obj_in=tag)

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
