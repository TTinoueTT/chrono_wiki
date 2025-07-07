from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..dependencies.hybrid_auth import require_admin, require_auth, require_moderator
from ..models.user import User
from ..services import PersonService

router = APIRouter(tags=["persons"])


def get_person_service() -> PersonService:
    """
    人物サービスのインスタンスを取得

    Returns:
        PersonService: 人物サービスのインスタンス
    """
    return PersonService()


@router.post(
    "/persons/",
    response_model=schemas.Person,
    status_code=status.HTTP_201_CREATED,
)
def create_person(
    person: schemas.PersonCreate,
    db: Session = Depends(get_db),
    person_service: PersonService = Depends(get_person_service),
    current_user: User = Depends(require_moderator),
):
    """
    人物を作成

    Args:
        person: 人物作成データ
        db: データベースセッション
        person_service: 人物サービス（DI）

    Returns:
        作成された人物

    Raises:
        HTTPException: バリデーションエラーまたは重複エラーの場合
    """
    try:
        return person_service.create_person(db, person)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/persons/", response_model=List[schemas.Person])
def read_persons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    person_service: PersonService = Depends(get_person_service),
    current_user: User = Depends(require_auth),
):
    """
    人物一覧を取得

    Args:
        skip: スキップ数
        limit: 取得上限数
        db: データベースセッション
        person_service: 人物サービス（DI）

    Returns:
        人物のリスト
    """
    return person_service.get_persons(db, skip=skip, limit=limit)


@router.get("/persons/{person_id}", response_model=schemas.Person)
def read_person(
    person_id: int,
    db: Session = Depends(get_db),
    person_service: PersonService = Depends(get_person_service),
    current_user: User = Depends(require_auth),
):
    """
    人物を取得

    Args:
        person_id: 人物ID
        db: データベースセッション
        person_service: 人物サービス（DI）

    Returns:
        人物データ

    Raises:
        HTTPException: 人物が見つからない場合
    """
    person = person_service.get_person(db, person_id)
    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )
    return person


@router.get("/persons/ssid/{ssid}", response_model=schemas.Person)
def read_person_by_ssid(
    ssid: str,
    db: Session = Depends(get_db),
    person_service: PersonService = Depends(get_person_service),
    current_user: User = Depends(require_auth),
):
    """
    SSIDで人物を取得

    Args:
        ssid: 人物のSSID
        db: データベースセッション
        person_service: 人物サービス（DI）

    Returns:
        人物データ

    Raises:
        HTTPException: 人物が見つからない場合
    """
    person = person_service.get_person_by_ssid(db, ssid)
    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )
    return person


@router.put("/persons/{person_id}", response_model=schemas.Person)
def update_person(
    person_id: int,
    person: schemas.PersonUpdate,
    db: Session = Depends(get_db),
    person_service: PersonService = Depends(get_person_service),
    current_user: User = Depends(require_moderator),
):
    """
    人物を更新

    Args:
        person_id: 人物ID
        person: 更新データ
        db: データベースセッション
        person_service: 人物サービス（DI）

    Returns:
        更新された人物データ

    Raises:
        HTTPException: 人物が見つからない場合またはバリデーションエラーの場合
    """
    try:
        updated_person = person_service.update_person(db, person_id, person)
        if updated_person is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person not found",
            )
        return updated_person
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/persons/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(
    person_id: int,
    db: Session = Depends(get_db),
    person_service: PersonService = Depends(get_person_service),
    current_user: User = Depends(require_admin),
):
    """
    人物を削除

    Args:
        person_id: 人物ID
        db: データベースセッション
        person_service: 人物サービス（DI）

    Raises:
        HTTPException: 人物が見つからない場合
    """
    success = person_service.delete_person(db, person_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )
