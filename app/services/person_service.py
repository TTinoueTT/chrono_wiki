"""
人物サービス

人物エンティティのビジネスロジックを実装します。
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from .. import schemas
from ..crud import person as crud
from .base import BaseService


class PersonService(BaseService):
    """
    人物サービス

    人物エンティティのビジネスロジックを実装します。
    """

    def __init__(self):
        """初期化"""
        super().__init__(crud)

    def create_person(
        self, db: Session, person: schemas.PersonCreate
    ) -> schemas.Person:
        """
        人物を作成

        Args:
            db: データベースセッション
            person: 人物作成データ

        Returns:
            作成された人物

        Raises:
            ValueError: SSIDが既に存在する場合
        """
        # ビジネスルール: SSIDの重複チェック
        existing_person = self.get_by_ssid(db, person.ssid)
        if existing_person:
            raise ValueError(f"SSID '{person.ssid}' is already registered")

        return self.create(db, obj_in=person)

    def get_person(
        self, db: Session, person_id: int
    ) -> Optional[schemas.Person]:
        """
        人物を取得

        Args:
            db: データベースセッション
            person_id: 人物ID

        Returns:
            人物またはNone
        """
        return self.get(db, person_id)

    def get_person_by_ssid(
        self, db: Session, ssid: str
    ) -> Optional[schemas.Person]:
        """
        SSIDで人物を取得

        Args:
            db: データベースセッション
            ssid: 人物のSSID

        Returns:
            人物またはNone
        """
        return self.get_by_ssid(db, ssid)

    def get_persons(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[schemas.Person]:
        """
        人物一覧を取得

        Args:
            db: データベースセッション
            skip: スキップ数
            limit: 取得上限数

        Returns:
            人物のリスト
        """
        return self.get_multi(db, skip=skip, limit=limit)

    def update_person(
        self, db: Session, person_id: int, person: schemas.PersonUpdate
    ) -> Optional[schemas.Person]:
        """
        人物を更新

        Args:
            db: データベースセッション
            person_id: 人物ID
            person: 更新データ

        Returns:
            更新された人物またはNone
        """
        return self.update(db, id=person_id, obj_in=person)

    def delete_person(self, db: Session, person_id: int) -> bool:
        """
        人物を削除

        Args:
            db: データベースセッション
            person_id: 人物ID

        Returns:
            削除成功フラグ
        """
        return self.remove(db, id=person_id)

    def validate_person_data(self, person: schemas.PersonCreate) -> None:
        """
        人物データのバリデーション

        Args:
            person: 人物データ

        Raises:
            ValueError: バリデーションエラーの場合
        """
        # ビジネスルール: 名前は必須
        if not person.full_name or not person.full_name.strip():
            raise ValueError("Full name is required")

        # ビジネスルール: SSIDは必須
        if not person.ssid or not person.ssid.strip():
            raise ValueError("SSID is required")

        # ビジネスルール: 生年月日と没年月日の整合性チェック
        if person.birth_date and person.death_date:
            if person.birth_date > person.death_date:
                raise ValueError("Birth date cannot be after death date")

    def get_persons_by_birth_year(
        self, db: Session, year: int, skip: int = 0, limit: int = 100
    ) -> List[schemas.Person]:
        """
        生年で人物を検索

        Args:
            db: データベースセッション
            year: 生年
            skip: スキップ数
            limit: 取得上限数

        Returns:
            人物のリスト
        """
        persons = crud.get_persons(db, skip=skip, limit=limit)
        return [
            schemas.Person.model_validate(p)
            for p in persons
            if p.birth_date.year == year
        ]
