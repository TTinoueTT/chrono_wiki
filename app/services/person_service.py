"""
人物サービス

人物エンティティのビジネスロジックを実装します。
シンプルなDI（依存性注入）パターンを使用してCRUD層との結合度を下げます。
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from .. import models, schemas
from ..crud.person import PersonCRUD
from .base import BaseService


class PersonService(BaseService[models.Person, schemas.PersonCreate, schemas.PersonUpdate]):
    """
    人物サービス

    人物エンティティのビジネスロジックを実装します。
    シンプルなDI（依存性注入）パターンを使用してCRUD層との結合度を下げます。
    """

    def __init__(self, person_crud=None):
        """
        初期化

        Args:
            person_crud: 人物CRUDオブジェクト（デフォルトでPersonCRUD()を使用）
        """
        if person_crud is None:
            person_crud = PersonCRUD()
        super().__init__(person_crud)

    def create_person(self, db: Session, person: schemas.PersonCreate) -> schemas.Person:
        """
        人物を作成

        Args:
            db: データベースセッション
            person: 人物作成データ

        Returns:
            作成された人物

        Raises:
            ValueError: SSIDが既に存在する場合、またはバリデーションエラーの場合
        """
        # ビジネスルール: データバリデーション
        self.validate_person_data(person)

        # ビジネスルール: SSIDの重複チェック
        existing_person = self.get_by_ssid(db, person.ssid)
        if existing_person:
            raise ValueError(f"SSID '{person.ssid}' is already registered")

        # CRUD操作を実行
        created_person = self.create(db, obj_in=person)

        # レスポンススキーマに変換
        return schemas.Person.model_validate(created_person)

    def get_person(self, db: Session, person_id: int) -> Optional[schemas.Person]:
        """
        人物を取得

        Args:
            db: データベースセッション
            person_id: 人物ID

        Returns:
            人物またはNone
        """
        person = self.get(db, person_id)
        if person:
            return schemas.Person.model_validate(person)
        return None

    def get_person_by_ssid(self, db: Session, ssid: str) -> Optional[schemas.Person]:
        """
        SSIDで人物を取得

        Args:
            db: データベースセッション
            ssid: 人物のSSID

        Returns:
            人物またはNone
        """
        person = self.get_by_ssid(db, ssid)
        if person:
            return schemas.Person.model_validate(person)
        return None

    def get_persons(self, db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Person]:
        """
        人物一覧を取得

        Args:
            db: データベースセッション
            skip: スキップ数
            limit: 取得上限数

        Returns:
            人物のリスト
        """
        persons = self.get_multi(db, skip=skip, limit=limit)
        return [schemas.Person.model_validate(p) for p in persons]

    def update_person(self, db: Session, person_id: int, person: schemas.PersonUpdate) -> Optional[schemas.Person]:
        """
        人物を更新

        Args:
            db: データベースセッション
            person_id: 人物ID
            person: 更新データ

        Returns:
            更新された人物またはNone

        Raises:
            ValueError: バリデーションエラーの場合
        """
        # ビジネスルール: 更新データのバリデーション
        self.validate_person_update_data(person)

        # CRUD操作を実行
        updated_person = self.update(db, id=person_id, obj_in=person)

        if updated_person:
            return schemas.Person.model_validate(updated_person)
        return None

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

    def validate_person_update_data(self, person: schemas.PersonUpdate) -> None:
        """
        人物更新データのバリデーション

        Args:
            person: 人物更新データ

        Raises:
            ValueError: バリデーションエラーの場合
        """
        # ビジネスルール: 生年月日と没年月日の整合性チェック（両方が指定されている場合）
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
        persons = self.get_multi(db, skip=skip, limit=limit)
        filtered_persons = [
            p for p in persons if hasattr(p, "birth_date") and p.birth_date and p.birth_date.year == year  # type: ignore
        ]
        return [schemas.Person.model_validate(p) for p in filtered_persons]

    def get_persons_by_country(
        self, db: Session, country: str, skip: int = 0, limit: int = 100
    ) -> List[schemas.Person]:
        """
        出生国で人物を検索

        Args:
            db: データベースセッション
            country: 出生国
            skip: スキップ数
            limit: 取得上限数

        Returns:
            人物のリスト
        """
        persons = self.get_multi(db, skip=skip, limit=limit)
        filtered_persons = [
            p for p in persons if hasattr(p, "born_country") and p.born_country and p.born_country.lower() == country.lower()  # type: ignore
        ]
        return [schemas.Person.model_validate(p) for p in filtered_persons]
