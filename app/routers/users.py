"""
ユーザー管理ルーター

ユーザーのCRUD操作と管理機能を提供します。
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..dependencies.auth import require_admin, require_auth, require_moderator
from ..models.user import User
from ..services.user import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[schemas.User])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """ユーザー一覧を取得（管理者のみ）"""
    users = user_service.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/active", response_model=List[schemas.User])
def get_active_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_moderator),
):
    """アクティブユーザー一覧を取得（モデレーター以上）"""
    users = user_service.get_active_users(db, skip=skip, limit=limit)
    return users


@router.get("/role/{role}", response_model=List[schemas.User])
def get_users_by_role(
    role: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_moderator),
):
    """役割別ユーザー一覧を取得（モデレーター以上）"""
    users = user_service.get_users_by_role(db, role, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schemas.User)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """ユーザー詳細を取得（自分自身または管理者のみ）"""
    # 自分自身または管理者のみアクセス可能
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    user = user_service.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: str,
    user_data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """ユーザーを更新（自分自身または管理者のみ）"""
    # 自分自身または管理者のみ更新可能
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    try:
        updated_user = user_service.update_user(db, user_id, user_data)
        if updated_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """ユーザーを削除（管理者のみ）"""
    success = user_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.post("/{user_id}/activate", response_model=schemas.User)
def activate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """ユーザーを有効化（管理者のみ）"""
    user = user_service.activate_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/{user_id}/deactivate", response_model=schemas.User)
def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """ユーザーを無効化（管理者のみ）"""
    user = user_service.deactivate_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/{user_id}/lock", response_model=schemas.User)
def lock_user_account(
    user_id: str,
    lock_minutes: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """ユーザーアカウントをロック（管理者のみ）"""
    user = user_service.lock_account(db, user_id, lock_minutes)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/{user_id}/unlock", response_model=schemas.User)
def unlock_user_account(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """ユーザーアカウントのロックを解除（管理者のみ）"""
    user = user_service.unlock_account(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/stats/count")
def get_user_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_moderator),
):
    """ユーザー統計情報を取得（モデレーター以上）"""
    total_users = user_service.count_users(db)
    active_users = user_service.count_active_users(db)

    return {"total_users": total_users, "active_users": active_users, "inactive_users": total_users - active_users}


@router.get("/stats/role/{role}/count")
def get_user_count_by_role(
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_moderator),
):
    """役割別ユーザー数を取得（モデレーター以上）"""
    count = user_service.count_users_by_role(db, role)
    return {"role": role, "count": count}
