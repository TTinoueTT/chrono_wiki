from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services import PersonService

router = APIRouter(prefix="/persons", tags=["persons"])

# サービスインスタンス
person_service = PersonService()


@router.post(
    "/",
    response_model=schemas.Person,
    status_code=status.HTTP_201_CREATED,
)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    """人物を作成"""
    try:
        # ビジネスロジックのバリデーション
        person_service.validate_person_data(person)
        return person_service.create_person(db, person)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=List[schemas.Person])
def read_persons(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """人物一覧を取得"""
    return person_service.get_persons(db, skip=skip, limit=limit)


@router.get("/{person_id}", response_model=schemas.Person)
def read_person(person_id: int, db: Session = Depends(get_db)):
    """人物を取得"""
    person = person_service.get_person(db, person_id)
    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    return person


@router.get("/ssid/{ssid}", response_model=schemas.Person)
def read_person_by_ssid(ssid: str, db: Session = Depends(get_db)):
    """SSIDで人物を取得"""
    person = person_service.get_person_by_ssid(db, ssid)
    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    return person


@router.put("/{person_id}", response_model=schemas.Person)
def update_person(
    person_id: int, person: schemas.PersonUpdate, db: Session = Depends(get_db)
):
    """人物を更新"""
    updated_person = person_service.update_person(db, person_id, person)
    if updated_person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    return updated_person


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    """人物を削除"""
    success = person_service.delete_person(db, person_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
