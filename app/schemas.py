from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """ユーザーの基本スキーマ"""

    email: EmailStr = Field(..., description="メールアドレス")
    username: str = Field(..., min_length=3, max_length=50, description="ユーザー名")
    full_name: Optional[str] = Field(default=None, max_length=100, description="本名")
    is_active: bool = Field(default=True, description="アカウント有効/無効")
    role: str = Field(default="user", description="ユーザー役割")
    avatar_url: Optional[str] = Field(default=None, max_length=500, description="プロフィール画像URL（更新時は任意）")
    bio: Optional[str] = Field(default=None, max_length=500, description="自己紹介（更新時は任意）")


class UserCreate(UserBase):
    """ユーザー作成用スキーマ"""

    password: str = Field(..., min_length=8, description="パスワード")


class UserUpdate(BaseModel):
    """ユーザー更新用スキーマ"""

    email: Optional[EmailStr] = Field(default=None, description="メールアドレス（更新時は任意）")
    username: Optional[str] = Field(default=None, min_length=3, max_length=50, description="ユーザー名（更新時は任意）")
    full_name: Optional[str] = Field(default=None, max_length=100, description="本名（更新時は任意）")
    is_active: Optional[bool] = Field(default=None, description="アカウント有効/無効（更新時は任意）")
    role: Optional[str] = Field(default=None, description="ユーザー役割（更新時は任意）")
    avatar_url: Optional[str] = Field(default=None, max_length=500, description="プロフィール画像URL（更新時は任意）")
    bio: Optional[str] = Field(default=None, max_length=500, description="自己紹介（更新時は任意）")


class User(BaseModel):
    """ユーザーレスポンススキーマ"""

    id: str
    created_at: datetime
    updated_at: datetime
    email: EmailStr = Field(..., description="メールアドレス")
    username: str = Field(..., min_length=3, max_length=50, description="ユーザー名")
    full_name: Optional[str] = Field(default=None, max_length=100, description="本名")
    avatar_url: Optional[str] = Field(default=None, max_length=500, description="プロフィール画像URL")
    bio: Optional[str] = Field(default=None, max_length=500, description="自己紹介")
    is_active: bool = Field(default=True, description="アカウント有効/無効")
    is_superuser: bool = Field(default=False, description="スーパーユーザーフラグ")
    role: str = Field(default="user", description="ユーザー役割")
    last_login: Optional[str] = Field(default=None, description="最終ログイン日時")
    failed_login_attempts: str = Field(default="0", description="ログイン失敗回数")
    locked_until: Optional[str] = Field(default=None, description="アカウントロック期限")

    class Config:
        from_attributes = True


class PersonBase(BaseModel):
    """人物の基本スキーマ"""

    ssid: str = Field(..., max_length=50, description="検索用識別子")
    full_name: str = Field(..., max_length=100, description="フルネーム")
    display_name: str = Field(..., max_length=50, description="表示名")
    birth_date: date = Field(..., description="生年月日")
    death_date: Optional[date] = Field(default=None, description="没年月日")
    born_country: str = Field(..., max_length=100, description="出生国")
    born_region: Optional[str] = Field(default=None, max_length=100, description="出生地域")
    description: Optional[str] = Field(default=None, description="説明")
    portrait_url: Optional[str] = Field(default=None, max_length=2048, description="肖像画URL")


class PersonCreate(PersonBase):
    """人物作成用スキーマ"""

    pass


class PersonUpdate(BaseModel):
    """人物更新用スキーマ"""

    full_name: Optional[str] = Field(default=None, max_length=100, description="フルネーム（更新時は任意）")
    display_name: Optional[str] = Field(default=None, max_length=50, description="表示名（更新時は任意）")
    birth_date: Optional[date] = Field(default=None, description="生年月日（更新時は任意）")
    death_date: Optional[date] = Field(default=None, description="没年月日（更新時は任意）")
    born_country: Optional[str] = Field(default=None, max_length=100, description="出生国（更新時は任意）")
    born_region: Optional[str] = Field(default=None, max_length=100, description="出生地域（更新時は任意）")
    description: Optional[str] = Field(default=None, description="説明（更新時は任意）")
    portrait_url: Optional[str] = Field(default=None, max_length=2048, description="肖像画URL（更新時は任意）")


class Person(BaseModel):
    """人物レスポンススキーマ"""

    id: int
    created_at: datetime
    updated_at: datetime
    ssid: str = Field(..., max_length=50, description="検索用識別子")
    full_name: str = Field(..., max_length=100, description="フルネーム")
    display_name: str = Field(..., max_length=50, description="表示名")
    birth_date: date = Field(..., description="生年月日")
    death_date: Optional[date] = Field(default=None, description="没年月日")
    born_country: str = Field(..., max_length=100, description="出生国")
    born_region: Optional[str] = Field(default=None, max_length=100, description="出生地域")
    description: Optional[str] = Field(default=None, description="説明")
    portrait_url: Optional[str] = Field(default=None, max_length=2048, description="肖像画URL")

    class Config:
        from_attributes = True


class TagBase(BaseModel):
    """タグの基本スキーマ"""

    ssid: str = Field(..., max_length=50, description="検索用識別子")
    name: str = Field(..., max_length=50, description="タグ名")
    description: Optional[str] = Field(None, description="説明")


class TagCreate(TagBase):
    """タグ作成用スキーマ"""

    pass


class TagUpdate(BaseModel):
    """タグ更新用スキーマ"""

    name: Optional[str] = Field(default=None, max_length=50, description="タグ名（更新時は任意）")
    description: Optional[str] = Field(default=None, description="説明（更新時は任意）")


class Tag(BaseModel):
    """タグレスポンススキーマ"""

    id: int
    created_at: datetime
    updated_at: datetime
    ssid: str = Field(..., max_length=50, description="検索用識別子")
    name: str = Field(..., max_length=50, description="タグ名")
    description: Optional[str] = Field(None, description="説明")

    class Config:
        from_attributes = True


class EventBase(BaseModel):
    """出来事の基本スキーマ"""

    ssid: str = Field(..., max_length=50, description="検索用識別子")
    title: str = Field(..., max_length=255, description="タイトル")
    start_date: date = Field(..., description="開始日")
    end_date: Optional[date] = Field(default=None, description="終了日")
    description: Optional[str] = Field(default=None, description="説明")
    location_name: Optional[str] = Field(default=None, max_length=255, description="場所名")
    latitude: Optional[float] = Field(default=None, ge=-90, le=90, description="緯度")
    longitude: Optional[float] = Field(default=None, ge=-180, le=180, description="経度")
    place_id: Optional[str] = Field(default=None, max_length=255, description="Google Places ID")
    image_url: Optional[dict] = Field(default=None, description="画像URL")


class EventCreate(EventBase):
    """出来事作成用スキーマ"""

    pass


class EventUpdate(BaseModel):
    """出来事更新用スキーマ"""

    title: Optional[str] = Field(default=None, max_length=255, description="タイトル（更新時は任意）")
    start_date: Optional[date] = Field(default=None, description="開始日（更新時は任意）")
    end_date: Optional[date] = Field(default=None, description="終了日（更新時は任意）")
    description: Optional[str] = Field(default=None, description="説明（更新時は任意）")
    location_name: Optional[str] = Field(default=None, max_length=255, description="場所名（更新時は任意）")
    latitude: Optional[float] = Field(default=None, ge=-90, le=90, description="緯度（更新時は任意）")
    longitude: Optional[float] = Field(default=None, ge=-180, le=180, description="経度（更新時は任意）")
    place_id: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Google Places ID（更新時は任意）",
    )
    image_url: Optional[dict] = Field(default=None, description="画像URL（更新時は任意）")


class Event(BaseModel):
    """出来事レスポンススキーマ"""

    id: int
    created_at: datetime
    updated_at: datetime
    ssid: str = Field(..., max_length=50, description="検索用識別子")
    title: str = Field(..., max_length=255, description="タイトル")
    start_date: date = Field(..., description="開始日")
    end_date: Optional[date] = Field(default=None, description="終了日")
    description: Optional[str] = Field(default=None, description="説明")
    location_name: Optional[str] = Field(default=None, max_length=255, description="場所名")
    latitude: Optional[float] = Field(default=None, ge=-90, le=90, description="緯度")
    longitude: Optional[float] = Field(default=None, ge=-180, le=180, description="経度")
    place_id: Optional[str] = Field(default=None, max_length=255, description="Google Places ID")
    image_url: Optional[dict] = Field(default=None, description="画像URL")

    class Config:
        from_attributes = True


# 認証関連スキーマ
class Token(BaseModel):
    """トークンレスポンススキーマ"""

    access_token: str = Field(..., description="アクセストークン")
    token_type: str = Field(default="bearer", description="トークンタイプ")
    expires_in: int = Field(..., description="有効期限（秒）")
    refresh_token: Optional[str] = Field(default=None, description="リフレッシュトークン")


class TokenData(BaseModel):
    """トークンデータスキーマ"""

    user_id: Optional[str] = Field(default=None, description="ユーザーID")
    email: Optional[str] = Field(default=None, description="メールアドレス")
    role: Optional[str] = Field(default=None, description="ユーザー役割")
    type: Optional[str] = Field(default=None, description="トークンタイプ")


class LoginRequest(BaseModel):
    """ログインリクエストスキーマ"""

    username: str = Field(..., description="ユーザー名またはメールアドレス")
    password: str = Field(..., description="パスワード")


class RefreshTokenRequest(BaseModel):
    """リフレッシュトークンリクエストスキーマ"""

    refresh_token: str = Field(..., description="リフレッシュトークン")


__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "User",
    "PersonBase",
    "PersonCreate",
    "PersonUpdate",
    "Person",
    "TagBase",
    "TagCreate",
    "TagUpdate",
    "Tag",
    "EventBase",
    "EventCreate",
    "EventUpdate",
    "Event",
    "Token",
    "TokenData",
    "LoginRequest",
    "RefreshTokenRequest",
]
