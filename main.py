from fastapi import FastAPI

app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/")
async def root():
    return {"message": "Hello World"}

# パスパラメータ
# 例: http://localhost:8000/items/123
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# クエリパラメータ
# 例: http://localhost:8000/items/?skip=0&limit=2
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

# オプショナルパラメータ
# 例: http://localhost:8000/users/123/items/123?q=test&short=true
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id, "user_id": user_id}
    if q:
        item.update({"q": q})
    if short:
        item.update({"short": True})
    return item