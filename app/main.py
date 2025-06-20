from fastapi import FastAPI

from .routers import events, persons, tags

app = FastAPI(title="Historical Figures API", version="1.0.0")

# ルーターを登録
app.include_router(persons.router)
app.include_router(tags.router)
app.include_router(events.router)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "Historical Figures API"}
