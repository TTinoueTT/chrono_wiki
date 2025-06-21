from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class PersonBase(BaseModel):
    """人物の基本スキーマ"""

    ssid: str = Field(..., max_length=50, description="検索用識別子")
    full_name: str = Field(..., max_length=100, description="フルネーム")
    display_name: str = Field(..., max_length=50, description="表示名")
    search_name: str = Field(..., max_length=255, description="検索用名")
    birth_date: date = Field(..., description="生年月日")
    death_date: Optional[date] = Field(None, description="没年月日")
    born_country: str = Field(..., max_length=100, description="出生国")
    born_region: Optional[str] = Field(
        None, max_length=100, description="出生地域"
    )
    description: Optional[str] = Field(None, description="説明")
    portrait_url: Optional[str] = Field(
        None, max_length=2048, description="肖像画URL"
    )


class PersonCreate(PersonBase):
    """人物作成用スキーマ"""

    pass


class PersonUpdate(BaseModel):
    """人物更新用スキーマ"""

    full_name: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, max_length=50)
    search_name: Optional[str] = Field(None, max_length=255)
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    born_country: Optional[str] = Field(None, max_length=100)
    born_region: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    portrait_url: Optional[str] = Field(None, max_length=2048)


class Person(PersonBase):
    """人物レスポンススキーマ"""

    id: int
    created_at: datetime
    updated_at: datetime

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

    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class Tag(TagBase):
    """タグレスポンススキーマ"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EventBase(BaseModel):
    """出来事の基本スキーマ"""

    ssid: str = Field(..., max_length=50, description="検索用識別子")
    title: str = Field(..., max_length=255, description="タイトル")
    start_date: date = Field(..., description="開始日")
    end_date: Optional[date] = Field(None, description="終了日")
    description: Optional[str] = Field(None, description="説明")
    location_name: Optional[str] = Field(
        None, max_length=255, description="場所名"
    )
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="緯度")
    longitude: Optional[float] = Field(
        None, ge=-180, le=180, description="経度"
    )
    place_id: Optional[str] = Field(
        None, max_length=255, description="Google Places ID"
    )
    image_url: Optional[dict] = Field(None, description="画像URL")


class EventCreate(EventBase):
    """出来事作成用スキーマ"""

    pass


class EventUpdate(BaseModel):
    """出来事更新用スキーマ"""

    title: Optional[str] = Field(None, max_length=255)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    location_name: Optional[str] = Field(None, max_length=255)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    place_id: Optional[str] = Field(None, max_length=255)
    image_url: Optional[dict] = None


class Event(EventBase):
    """出来事レスポンススキーマ"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
