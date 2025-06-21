from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..crud import person as crud
from ..database import get_db

router = APIRouter(prefix="/persons", tags=["persons"])


@router.post(
    "/",
    response_model=schemas.Person,
    status_code=status.HTTP_201_CREATED,
)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    """人物を作成"""
    db_person = crud.get_person_by_ssid(db, ssid=person.ssid)
    if db_person:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SSID already registered",
        )
    return crud.create_person(db=db, person=person)


@router.get("/", response_model=List[schemas.Person])
def read_persons(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """人物一覧を取得"""
    persons = crud.get_persons(db, skip=skip, limit=limit)
    return persons


@router.get("/{person_id}", response_model=schemas.Person)
def read_person(person_id: int, db: Session = Depends(get_db)):
    """人物を取得"""
    db_person = crud.get_person(db, person_id=person_id)
    if db_person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    return db_person


@router.get("/ssid/{ssid}", response_model=schemas.Person)
def read_person_by_ssid(ssid: str, db: Session = Depends(get_db)):
    """SSIDで人物を取得"""
    db_person = crud.get_person_by_ssid(db, ssid=ssid)
    if db_person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    return db_person


@router.put("/{person_id}", response_model=schemas.Person)
def update_person(
    person_id: int, person: schemas.PersonUpdate, db: Session = Depends(get_db)
):
    """人物を更新"""
    db_person = crud.update_person(db, person_id=person_id, person=person)
    if db_person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    return db_person


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    """人物を削除"""
    success = crud.delete_person(db, person_id=person_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
