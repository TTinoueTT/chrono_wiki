from fastapi import Depends, FastAPI

from .dependencies.authorization import verify_token
from .routers import auth, events, persons, tags, users

app = FastAPI(
    title="Historical Figures API",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "ユーザー認証に関する操作。",
        },
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
        {
            "name": "users",
            "description": "ユーザー管理に関する操作。",
        },
    ],
)

# 認証ルーターを最初に登録（認証不要）
app.include_router(auth.router)

# その他のルーターを登録（API-Key認証が必要）
app.include_router(persons.router, dependencies=[Depends(verify_token)])
app.include_router(tags.router, dependencies=[Depends(verify_token)])
app.include_router(events.router, dependencies=[Depends(verify_token)])
app.include_router(users.router, dependencies=[Depends(verify_token)])


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "Historical Figures API"}
