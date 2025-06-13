from typing import Annotated, Literal
from fastapi import FastAPI, Query
from typing import Union
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None

class FilterParams(BaseModel):
    model_config = {"extra": "forbid"} # 余分なパラメータを禁止
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


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
async def read_items(
    q: Union[str, None] = Query(
        default=None,
        alias="item-query",
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
        min_length=3,
        max_length=50,
        pattern="^fixedquery$",
        deprecated=True,
    ),
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

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

# ボディ付きのPOSTリクエスト(pydanticのモデルを使用)
# 例: http://localhost:8000/items/
@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump() # dict型に変換
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        # 辞書にキー("price_with_tax")と値を追加
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

# クエリパラメータに Pydantic モデルを使用
@app.get("/items2/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query