# 設定ガイド

このドキュメントでは、年表サービスAPIの環境変数と設定ファイルについて詳しく説明します。

## 📝 環境変数の設定

### 必須環境変数
```bash
# データベース設定
POSTGRES_DB=historical_figures
POSTGRES_USER=fastapi_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_PORT=5432

# テスト用データベース設定
TEST_POSTGRES_DB=historical_figures_test
TEST_POSTGRES_USER=fastapi_test_user
TEST_POSTGRES_PASSWORD=your_test_password
TEST_POSTGRES_PORT=5433

# API設定
API_PORT=8020
API_INTERNAL_PORT=8000
API_HOST=0.0.0.0

# 環境設定
ENVIRONMENT=development
DEBUG=1
```

### オプション環境変数
```bash
# ログレベル
LOG_LEVEL=INFO

# セッション設定
SECRET_KEY=your_secret_key

# 外部API設定
EXTERNAL_API_URL=https://api.example.com
EXTERNAL_API_KEY=your_api_key

# データベース接続設定
DATABASE_URL=postgresql://fastapi_user:your_secure_password@postgres:5432/historical_figures
TEST_DATABASE_URL=postgresql://fastapi_test_user:your_test_password@test_postgres:5432/historical_figures_test
```

## 🔧 設定ファイル

### .env ファイル
プロジェクトルートに `.env` ファイルを作成して環境変数を設定します。

```bash
# .env ファイルの例
# データベース設定
POSTGRES_DB=historical_figures
POSTGRES_USER=fastapi_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_PORT=5432

# テスト用データベース設定
TEST_POSTGRES_DB=historical_figures_test
TEST_POSTGRES_USER=fastapi_test_user
TEST_POSTGRES_PASSWORD=your_test_password
TEST_POSTGRES_PORT=5433

# API設定
API_PORT=8020
API_INTERNAL_PORT=8000
API_HOST=0.0.0.0

# 環境設定
ENVIRONMENT=development
DEBUG=1

# ログ設定
LOG_LEVEL=INFO

# セキュリティ設定
SECRET_KEY=your-super-secret-key-here
```

### .env.example ファイル
`.env.example` ファイルは、必要な環境変数のテンプレートとして機能します。

```bash
# .env.example ファイルの例
# データベース設定
POSTGRES_DB=historical_figures
POSTGRES_USER=fastapi_user
POSTGRES_PASSWORD=change_me
POSTGRES_PORT=5432

# テスト用データベース設定
TEST_POSTGRES_DB=historical_figures_test
TEST_POSTGRES_USER=fastapi_test_user
TEST_POSTGRES_PASSWORD=change_me
TEST_POSTGRES_PORT=5433

# API設定
API_PORT=8020
API_INTERNAL_PORT=8000
API_HOST=0.0.0.0

# 環境設定
ENVIRONMENT=development
DEBUG=1

# ログ設定
LOG_LEVEL=INFO

# セキュリティ設定
SECRET_KEY=change_me_to_a_secure_random_string
```

## 🐳 Docker Compose設定

### 開発環境 (docker-compose.dev.yml)
```yaml
version: "3.8"

services:
  postgres:
    image: postgres:17
    container_name: fastapi_postgres
    restart: always
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    ports:
      - "${POSTGRES_PORT}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    command: >
      postgres -c shared_preload_libraries='pg_stat_statements' -c max_connections=200 -c shared_buffers=256MB -c effective_cache_size=1GB -c maintenance_work_mem=64MB -c checkpoint_completion_target=0.9 -c wal_buffers=16MB -c default_statistics_target=100 -c random_page_cost=1.1 -c effective_io_concurrency=200
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}" ]
      timeout: 20s
      retries: 10

  test_postgres:
    image: postgres:17
    container_name: fastapi_test_postgres
    restart: "no"
    environment:
      POSTGRES_DB: ${TEST_POSTGRES_DB}
      POSTGRES_USER: ${TEST_POSTGRES_USER}
      POSTGRES_PASSWORD: ${TEST_POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    ports:
      - "${TEST_POSTGRES_PORT}:5432"
    volumes:
      - test_postgres_data:/var/lib/postgresql/data
    command: >
      postgres -c shared_preload_libraries='pg_stat_statements' -c max_connections=50 -c shared_buffers=128MB -c effective_cache_size=512MB -c maintenance_work_mem=32MB -c checkpoint_completion_target=0.9 -c wal_buffers=8MB -c default_statistics_target=50 -c random_page_cost=1.1 -c effective_io_concurrency=100
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U ${TEST_POSTGRES_USER} -d ${TEST_POSTGRES_DB}" ]
      timeout: 10s
      retries: 5
    profiles:
      - test

  api:
    build:
      context: .
      args:
        ENVIRONMENT: ${ENVIRONMENT}
    ports:
      - "${API_PORT}:${API_INTERNAL_PORT}"
    volumes:
      - .:/app
      - ${HOME}/.ssh:/root/.ssh:delegated
      - ${HOME}/.gnupg:/root/.gnupg:delegated
    env_file:
      - .env
    environment:
      - ENVIRONMENT=${ENVIRONMENT}
      - DEBUG=${DEBUG}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - TEST_DATABASE_URL=postgresql://${TEST_POSTGRES_USER}:${TEST_POSTGRES_PASSWORD}@test_postgres:5432/${TEST_POSTGRES_DB}
      - PGPASSWORD=${POSTGRES_PASSWORD}
    depends_on:
      postgres:
        condition: service_healthy
    command: uvicorn app.main:app --host ${API_HOST} --port ${API_INTERNAL_PORT} --reload

volumes:
  postgres_data:
  test_postgres_data:
```

## 📊 ワーカー数の設定

### ワーカーとは
- アプリケーションのインスタンス
- リクエストを処理するプロセス
- 並行して動作する

### 環境ごとのワーカー設定

#### 1. 開発環境
```yaml
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **ワーカー数**: 1（デフォルト）
- **理由**: デバッグしやすく、ホットリロードのため

#### 2. ステージング環境
```yaml
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```
- **ワーカー数**: 2
- **理由**: 本番に近い環境でテスト

#### 3. 本番環境
```yaml
command: gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
- **ワーカー数**: 4
- **理由**: 高負荷に対応

### ワーカー数の決め方
```python
# 一般的な計算式
workers = (2 × CPUコア数) + 1
```

### メリット
1. **並行処理**: 複数のリクエストを同時に処理
2. **可用性**: 1つのワーカーがクラッシュしても他が動作
3. **リソース活用**: CPUコアを効率的に使用

### 注意点
1. **メモリ使用量**: ワーカー数↑ = メモリ使用量↑
2. **共有リソース**: ワーカー間で共有リソースに注意
3. **デバッグ**: 複数ワーカーはデバッグを複雑に

## 🔄 共有リソースの注意点

### 主な注意点

#### 1. データベース接続
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

#### 2. キャッシュ
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

#### 3. セッション管理
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

### 解決策

#### 1. 外部サービスの利用
- **Redis**: キャッシュ、セッション
- **Memcached**: キャッシュ
- **データベース**: 状態管理

#### 2. 適切なミドルウェア
```python
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
```

#### 3. 依存性注入
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

## 🔒 セキュリティ設定

### 環境変数のセキュリティ
```bash
# 本番環境では必ず変更
SECRET_KEY=your-super-secret-key-here
POSTGRES_PASSWORD=your-very-secure-password

# 環境変数の暗号化（オプション）
# 本番環境では環境変数管理サービスを使用
```

### データベースセキュリティ
```yaml
# PostgreSQL設定
postgres:
  environment:
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  # 本番環境では追加のセキュリティ設定
  # - SSL設定
  # - ネットワークアクセス制限
  # - 認証設定
```

## 📝 設定の検証

### 環境変数の確認
```bash
# 環境変数が正しく設定されているか確認
docker compose -f docker-compose.dev.yml config

# 特定の環境変数を確認
echo $POSTGRES_DB
echo $API_PORT
```

### 設定ファイルの検証
```bash
# Docker Compose設定の検証
docker compose -f docker-compose.dev.yml config --quiet

# 環境変数ファイルの確認
cat .env | grep -v '^#' | grep -v '^$'
```

## 🔗 関連リンク

- [インストール手順](./installation.md)
- [トラブルシューティング](./troubleshooting.md)
- [プロジェクトREADME](../../README.md)

---

**注意**: 本番環境では、セキュリティ設定やパフォーマンスチューニングを必ず行ってください。 