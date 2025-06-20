# 年表サービス API

歴史的人物とイベントの年表データを管理・検索するためのRESTful APIサービスです。

## プロジェクト概要

### 目的
- 歴史的人物の生涯と関連イベントの時系列データ管理
- 人物・イベント・タグの関連性を表現するリレーショナルデータベース
- 柔軟な検索・フィルタリング機能の提供

### 技術スタック
- **Backend**: FastAPI (Python 3.13)
- **Database**: PostgreSQL 17.x
- **ORM**: SQLAlchemy
- **Migration**: Alembic
- **Container**: Docker & Docker Compose
- **Testing**: pytest

## データベース選定: PostgreSQL 17

### バージョン選定理由

#### PostgreSQL 17の採用理由
- **最新のパフォーマンス改善**: バキュームプロセス、I/O層、クエリ実行の大幅な高速化
- **年表データに最適な新機能**: 
  - **MERGE機能**: 人物・イベント情報の効率的な更新
  - **JSONB機能拡張**: メタデータの柔軟な管理
  - **コピー機能改善**: 大量データの高速インポート
- **高可用性の強化**: 論理レプリケーションの改善でゼロダウンタイム運用
- **セキュリティ・監視の向上**: 運用負荷の軽減

### 選定理由

#### 1. 年表データの特性に最適
- **日付・時刻型の強力なサポート**: `date`, `timestamp`, `interval`型で時系列データを正確に管理
- **ウィンドウ関数・CTE**: 「この期間の前後のイベント」「人物の生涯年表」などの複雑なクエリが高速
- **JSONB型**: 柔軟なメタデータ（画像URL、地理情報、説明文）の保存

#### 2. 検索・分析機能の拡張性
- **全文検索**: イベントや人物の説明文の高度な検索
- **地理情報拡張（PostGIS）**: 将来的な地図連携機能への対応
- **複雑なJOIN**: 人物・イベント・タグの多対多リレーションの高速処理

#### 3. データ整合性と信頼性
- **ACID準拠**: 年表データの一貫性を厳密に保証
- **外部キー制約**: リレーションの整合性を自動的に維持
- **トランザクション管理**: 複数テーブルへの同時更新の安全性

#### 4. 標準SQL準拠
- **SQL標準準拠度の高さ**: 将来的な移行や他システムとの連携が容易
- **豊富な関数・演算子**: 日付計算、文字列処理、集計関数が充実

### PostgreSQL 17の最適化設定

#### 開発環境での設定
```yaml
# docker-compose.dev.yml
postgres:
  image: postgres:17
  command: >
    postgres
    -c shared_preload_libraries='pg_stat_statements'
    -c max_connections=200
    -c shared_buffers=256MB
    -c effective_cache_size=1GB
    -c maintenance_work_mem=64MB
    -c checkpoint_completion_target=0.9
    -c wal_buffers=16MB
    -c default_statistics_target=100
    -c random_page_cost=1.1
    -c effective_io_concurrency=200
```

#### 年表サービス向けの最適化ポイント
- **shared_buffers**: 256MBでメモリ内キャッシュを確保
- **effective_cache_size**: 1GBでOSキャッシュの活用
- **maintenance_work_mem**: 64MBでバキューム・インデックス作成の高速化
- **effective_io_concurrency**: 200で並列I/O処理の最適化

### 代替案との比較

| 項目 | PostgreSQL 17 | PostgreSQL 15 | MySQL 8.0 | SQLite |
|------|---------------|---------------|-----------|--------|
| 時系列データ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 複雑なクエリ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| 拡張性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| 標準準拠 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 最新機能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| 運用コスト | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### 将来の拡張予定
- **全文検索機能**: イベント・人物の説明文の高度な検索
- **地理情報連携**: イベント発生地の地図表示（PostGIS拡張）
- **統計・分析機能**: 時代別・地域別の統計情報
- **API連携**: 外部の歴史データベースとの連携
- **リアルタイム更新**: PostgreSQL 17の論理レプリケーションを活用

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
