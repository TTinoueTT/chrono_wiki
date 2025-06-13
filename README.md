## Open API ドキュメント

|title|URI|説明|
|:---:|:---:|:---:|
|ドキュメント|http://localhost:8000/docs|APIドキュメントリスト|
|JSONスキーマ|http://localhost:8000/openapi.json|生成された JSON スキーマの表示|


## 関連ファイル紹介
### requirements.txt
Pythonプロジェクトの依存関係（パッケージ）を管理するためのファイル
- プロジェクトが必要とするパッケージとそのバージョンを明示
- 異なる環境でも同じ動作を保証するため(環境の再現性)

バージョン指定の方法
|記法|意味|例|
|---|---|---|
|`==`|完全一致|（例：`fastapi==0.109.2`）|
|`>=`|以上|（例：`fastapi>=0.109.2`）|
|`~=`|互換性のある場所|（例：`fastapi~=0.109.2`）|

#### 利用方法
```bash
   # 全パッケージをインストール
   pip install -r requirements.txt

   # Dockerfileでの使用例
   COPY requirements.txt .
   RUN pip install -r requirements.txt
```

### docker-compose.yaml

```bash
# 開発環境
docker-compose -f docker-compose.dev.yml up --build

# ステージング環境
docker-compose -f docker-compose.stg.yml up --build

# 本番環境
docker-compose -f docker-compose.prod.yml up --build
```

#### 開発環境 (docker-compose.dev.yml):
- ホットリロード有効
- ソースコードのマウント
- デバッグモード有効
- ポート: 8020
#### ステージング環境 (docker-compose.stg.yml):
- 本番に近い設定
- 2ワーカー
- デバッグモード無効
- ポート: 8030
#### 本番環境 (docker-compose.prod.yml):
- Gunicorn使用
- 4ワーカー
- デバッグモード無効
- ポート: 8040

#### 複数ワーカーについて
複数ワーカーについて説明します。

**ワーカーとは**:
- アプリケーションのインスタンス
- リクエストを処理するプロセス
- 並行して動作する

**環境ごとのワーカー設定**:

1. **開発環境** (`docker-compose.dev.yml`):
```yaml
command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
- ワーカー数: 1（デフォルト）
- 理由: デバッグしやすく、ホットリロードのため

2. **ステージング環境** (`docker-compose.stg.yml`):
```yaml
command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```
- ワーカー数: 2
- 理由: 本番に近い環境でテスト

3. **本番環境** (`docker-compose.prod.yml`):
```yaml
command: gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
- ワーカー数: 4
- 理由: 高負荷に対応

**ワーカー数の決め方**:
```python
# 一般的な計算式
workers = (2 × CPUコア数) + 1
```

**メリット**:
1. **並行処理**:
   - 複数のリクエストを同時に処理
   - レスポンス時間の改善

2. **可用性**:
   - 1つのワーカーがクラッシュしても他が動作
   - システムの安定性向上

3. **リソース活用**:
   - CPUコアを効率的に使用
   - パフォーマンスの最適化

**注意点**:
1. **メモリ使用量**:
   - ワーカー数↑ = メモリ使用量↑
   - サーバーのリソースに応じて調整

2. **共有リソース**:
   - ワーカー間で共有リソースに注意
   - 例：データベース接続、キャッシュ

3. **デバッグ**:
   - 複数ワーカーはデバッグを複雑に
   - 開発時は1ワーカーが推奨

このように、環境や用途に応じて適切なワーカー数を設定することが重要です。

## 共有リソースの注意点
複数ワーカーでの共有リソースの注意点について説明します。

**主な注意点**:

1. **データベース接続**:
```python
# 問題のある実装
db_connection = create_connection()  # グローバル変数

# 推奨される実装
def get_db():
    db = create_connection()
    try:
        yield db
    finally:
        db.close()
```

2. **キャッシュ**:
```python
# 問題のある実装
cache = {}  # グローバル変数

# 推奨される実装
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
```

3. **セッション管理**:
```python
# 問題のある実装
sessions = {}  # グローバル変数

# 推奨される実装
from fastapi_session import SessionMiddleware
from fastapi_session.backends.redis import RedisBackend

app.add_middleware(
    SessionMiddleware,
    backend=RedisBackend(redis_client),
    secret_key="your-secret-key"
)
```

4. **ファイル操作**:
```python
# 問題のある実装
with open("file.txt", "a") as f:
    f.write("data")  # 複数ワーカーで競合

# 推奨される実装
import fcntl
with open("file.txt", "a") as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    f.write("data")
    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

5. **メモリキャッシュ**:
```python
# 問題のある実装
CACHE = {}  # グローバル変数

# 推奨される実装
from fastapi_cache import FastAPICache
from fastapi_cache.backends.memory import InMemoryBackend

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())
```

**解決策**:

1. **外部サービスの利用**:
   - Redis: キャッシュ、セッション
   - Memcached: キャッシュ
   - データベース: 状態管理

2. **適切なミドルウェア**:
```python
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
```

3. **依存性注入**:
```python
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items/")
def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

4. **非同期処理**:
```python
from fastapi import BackgroundTasks

@app.post("/items/")
async def create_item(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_item)
    return {"message": "Processing started"}
```

**ベストプラクティス**:

1. **ステートレス設計**:
   - ワーカー間で状態を共有しない
   - 外部サービスで状態管理

2. **適切なロック機構**:
   - 分散ロック
   - トランザクション管理

3. **モニタリング**:
   - リソース使用量の監視
   - パフォーマンスメトリクスの収集

4. **エラーハンドリング**:
   - リトライメカニズム
   - フォールバック戦略

これらの注意点を考慮することで、複数ワーカー環境でも安全に動作するアプリケーションを構築できます。
