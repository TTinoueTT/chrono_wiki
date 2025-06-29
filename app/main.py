from fastapi import Depends, FastAPI

from .dependencies.authorization import verify_token
from .routers import events, persons, tags

app = FastAPI(
    title="Historical Figures API",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "persons",
            "description": "歴史的人物の管理に関する操作。",
        },
        {
            "name": "events",
            "description": "歴史的イベントの管理に関する操作。",
        },
        {
            "name": "tags",
            "description": "タグの管理に関する操作。",
        },
    ],
    dependencies=[Depends(verify_token)],  # グローバル認証を追加
)

# ルーターを登録
app.include_router(persons.router)
app.include_router(tags.router)
app.include_router(events.router)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "Historical Figures API"}
