"""
認証ルーター

ユーザー登録、ログイン、トークン管理などの認証関連APIを提供します。
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import schemas
from ..auth.utils import create_access_token, create_refresh_token, get_token_expires_in, verify_password
from ..database import get_db
from ..dependencies.auth import get_current_active_user
from ..models.user import User
from ..services.user import user_service

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """ユーザー登録"""
    try:
        user = user_service.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """ログイン"""
    # ユーザー検索（メールアドレスまたはユーザー名で）
    user = user_service.get_user_by_email(db, form_data.username)
    if not user:
        user = user_service.get_user_by_username(db, form_data.username)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")

    # アカウントロックチェック
    if user.locked_until:
        from datetime import datetime

        lock_time = datetime.fromisoformat(user.locked_until)
        if lock_time > datetime.now():
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Account temporarily locked")

    # パスワード検証
    if not verify_password(form_data.password, user.hashed_password):
        # 失敗回数を増加
        user_service.increment_failed_attempts(db, user.id)

        # 5回失敗でアカウントロック
        failed_attempts = int(user.failed_login_attempts or "0") + 1
        if failed_attempts >= 5:
            user_service.lock_account(db, user.id, lock_minutes=30)

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")

    # ログイン成功時の処理
    user_service.update_last_login(db, user.id)
    user_service.reset_failed_attempts(db, user.id)

    # トークン生成
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role}, expires_delta=access_token_expires
    )

    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": get_token_expires_in(),
        "refresh_token": refresh_token,
    }


@router.post("/refresh", response_model=schemas.Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """トークン更新"""
    from ..auth.utils import verify_token

    payload = verify_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = user_service.get_user(db, user_id)

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    # 新しいアクセストークン生成
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "expires_in": get_token_expires_in()}


@router.get("/me", response_model=schemas.User)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """現在のユーザー情報取得"""
    return current_user


@router.put("/me", response_model=schemas.User)
def update_current_user(
    user_data: schemas.UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """現在のユーザー情報を更新"""
    try:
        updated_user = user_service.update_user(db, current_user.id, user_data)
        if updated_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/logout")
def logout(current_user: User = Depends(get_current_active_user)):
    """ログアウト"""
    # オプション: トークンブラックリストに追加
    return {"message": "Logged out successfully"}


@router.post("/change-password")
def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """パスワード変更"""
    # 現在のパスワードを検証
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")

    # 新しいパスワードのバリデーション
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password must be at least 8 characters long"
        )

    # 新しいパスワードを設定
    updated_user = user_service.update_password(db, current_user.id, new_password)
    if updated_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"message": "Password changed successfully"}
