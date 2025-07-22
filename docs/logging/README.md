# FastAPI ログ設定ガイド

## 📋 概要

本ガイドでは、FastAPIアプリケーションの包括的なログ設定について説明します。参考リンクのベストプラクティスに基づいて実装されたログシステムにより、アプリケーションの動作監視、デバッグ、パフォーマンス分析が可能になります。

## 🚀 `/api/v1/demo` エンドポイントの利用用途

### **デモエンドポイントの説明**

`/api/v1/demo` エンドポイントは、ログ設定の動作確認とテストを目的として実装されています。各エンドポイントは特定のログ機能をデモンストレーションし、実際のログ出力を確認できます。

### **各エンドポイントの詳細**

#### **1. `/api/v1/demo/logging` - 基本ログデモ**
```bash
curl http://localhost:8000/api/v1/demo/logging
```

**利用用途**: 基本的なログレベルの動作確認
- 各ログレベル（DEBUG、INFO、WARNING、ERROR）の出力テスト
- ログ設定の基本動作確認

**ログ出力例**:
```
2025-07-07 14:07:35 - app.routers.demo - INFO - ログデモエンドポイントが呼び出されました
2025-07-07 14:07:35 - app.routers.demo - INFO - これはINFOレベルのログです
2025-07-07 14:07:35 - app.routers.demo - WARNING - これはWARNINGレベルのログです
2025-07-07 14:07:35 - app.routers.demo - ERROR - これはERRORレベルのログです
```

#### **2. `/api/v1/demo/auth-logging` - 認証ログデモ**
```bash
curl http://localhost:8000/api/v1/demo/auth-logging
```

**利用用途**: 認証関連のログ出力確認
- 認証イベントのログ記録テスト
- `logs/auth.log` への出力確認

**ログ出力例**:
```
2025-07-07 14:07:35 - app.auth - INFO - 認証ログデモ: ユーザーログイン試行
2025-07-07 14:07:35 - app.auth - WARNING - 認証ログデモ: 無効なパスワード試行
2025-07-07 14:07:35 - app.auth - ERROR - 認証ログデモ: アカウントロック
```

#### **3. `/api/v1/demo/service-logging` - サービスログデモ**
```bash
curl http://localhost:8000/api/v1/demo/service-logging
```

**利用用途**: サービス層のログ出力確認
- ビジネスロジックの実行ログ
- データベース操作の追跡

**ログ出力例**:
```
2025-07-07 14:07:35 - app.services - INFO - サービスログデモ: データベース接続確立
2025-07-07 14:07:35 - app.services - INFO - サービスログデモ: クエリ実行開始
2025-07-07 14:07:35 - app.services - INFO - サービスログデモ: クエリ実行完了
```

#### **4. `/api/v1/demo/crud-logging` - CRUDログデモ**
```bash
curl http://localhost:8000/api/v1/demo/crud-logging
```

**利用用途**: データベース操作のログ確認
- CRUD操作の実行ログ
- SQLクエリのデバッグ情報

#### **5. `/api/v1/demo/error-logging` - エラーログデモ**
```bash
curl http://localhost:8000/api/v1/demo/error-logging
```

**利用用途**: エラーハンドリングのログ確認
- 例外処理のログ記録
- `logs/error.log` への出力確認

**ログ出力例**:
```
2025-07-07 14:07:35 - app.routers.demo - ERROR - エラーログデモ: ゼロ除算エラーが発生しました: division by zero
```

#### **6. `/api/v1/demo/request-info` - リクエスト情報デモ**
```bash
curl http://localhost:8000/api/v1/demo/request-info
```

**利用用途**: リクエスト情報のログ記録確認
- HTTPメソッド、URL、IPアドレス、User-Agentの記録
- リクエスト追跡のテスト

#### **7. `/api/v1/demo/performance-logging` - パフォーマンスログデモ**
```bash
curl -X POST http://localhost:8000/api/v1/demo/performance-logging
```

**利用用途**: パフォーマンス監視のログ確認
- 処理時間の測定と記録
- パフォーマンス分析のテスト

#### **8. `/api/v1/demo/structured-logging` - 構造化ログデモ**
```bash
curl http://localhost:8000/api/v1/demo/structured-logging
```

**利用用途**: 構造化ログの出力確認
- JSON形式でのログ出力
- 機械学習や分析ツールでの利用

#### **9. `/api/v1/demo/log-levels` - ログレベル別デモ**
```bash
curl http://localhost:8000/api/v1/demo/log-levels
```

**利用用途**: 全ログレベルの動作確認
- DEBUG、INFO、WARNING、ERROR、CRITICALの出力テスト

## 📁 ログ設定の構成

### **実装したファイル構成**

```
app/
├── core/
│   ├── __init__.py          # コアパッケージ初期化
│   └── logging.py           # ログ設定ファイル
├── middleware/
│   └── logging.py           # リクエストログミドルウェア
├── routers/
│   └── demo_logging.py      # ログデモルーター
└── main.py                  # アプリケーション初期化
```

### **ログ設定の特徴**

#### 1. **環境別設定**
- **開発環境**: `DEBUG` - 詳細なログ
- **本番環境**: `INFO` - 重要なログのみ  
- **テスト環境**: `WARNING` - 警告以上のみ

#### 2. **ログ出力先**
- `logs/app.log`: アプリケーション全体のログ
- `logs/error.log`: エラーログのみ
- `logs/access.log`: アクセスログ（JSON形式）
- `logs/auth.log`: 認証ログ
- コンソール出力: 開発時の確認用

#### 3. **ローテーション設定**
- ファイルサイズ: 10MB
- バックアップ数: 5世代
- 自動ローテーション

## 🔧 ロギング設定ファイルの解説

### **`get_logging_config` の `loggers` に対する `handler` の説明**

```python
"loggers": {
    "app.middleware": {  # ミドルウェアロガー
        "handlers": ["console", "file", "access_file"],
        "level": log_level,
        "propagate": False,
    },
    "app.routers": {  # ルーターロガー
        "handlers": ["console", "file", "access_file"],
        "level": log_level,
        "propagate": False,
    },
    "app.auth": {  # 認証ロガー
        "handlers": ["console", "file", "error_file", "auth_file"],
        "level": log_level,
        "propagate": False,
    },
}
```

### **ハンドラーの定義**

```python
"handlers": {
    "console": {
        "class": "logging.StreamHandler",
        "level": log_level,
        "formatter": "detailed",
        "stream": "ext://sys.stdout",
    },
    "file": {
        "class": "logging.handlers.RotatingFileHandler",
        "level": log_level,
        "formatter": "detailed",
        "filename": "logs/app.log",
        "maxBytes": 10485760,  # 10MB
        "backupCount": 5,
    },
    "access_file": {
        "class": "logging.handlers.RotatingFileHandler",
        "level": "INFO",
        "formatter": "json",
        "filename": "logs/access.log",
        "maxBytes": 10485760,  # 10MB
        "backupCount": 5,
    },
    "auth_file": {
        "class": "logging.handlers.RotatingFileHandler",
        "level": "INFO",
        "formatter": "detailed",
        "filename": "logs/auth.log",
        "maxBytes": 10485760,  # 10MB
        "backupCount": 5,
    },
}
```

### **ミドルウェアのログが複数ファイルに出力される仕組み**

#### **1. ロガー名の階層構造**
```python
# app/middleware/logging.py
self.logger = get_logger("middleware.logging")
# 実際のロガー名: "app.middleware.logging"
```

#### **2. 設定マッチング**
```python
"app.middleware": {  # "app.middleware.logging" がこの設定にマッチ
    "handlers": ["console", "file", "access_file"],
    "level": log_level,
    "propagate": False,
},
```

#### **3. 出力先の決定**
- **`console`**: 標準出力（開発時の確認用）
- **`file`**: `logs/app.log`（詳細フォーマット）
- **`access_file`**: `logs/access.log`（JSON形式）

#### **4. 実際の出力例**

**app.log**:
```
2025-07-07 14:07:35 - app.middleware.logging - INFO - 受信リクエスト: GET /api/v1/demo/logging - IP: 192.168.65.1
```

**access.log**:
```json
{"timestamp": "2025-07-07 14:07:35", "level": "INFO", "logger": "app.middleware.logging", "message": "受信リクエスト: GET /api/v1/demo/logging - IP: 192.168.65.1"}
```

**コンソール**:
```
2025-07-07 14:07:35 - app.middleware.logging - INFO - 受信リクエスト: GET /api/v1/demo/logging - IP: 192.168.65.1
```

## 🐛 デバッグログを仕込む例

### **1. ルーターでのデバッグログ**

```python
# app/routers/persons.py
from ..core import get_logger

logger = get_logger("routers.persons")

@router.get("/persons/")
async def get_persons(skip: int = 0, limit: int = 100):
    logger.debug(f"人物一覧取得開始: skip={skip}, limit={limit}")
    
    try:
        persons = person_service.get_persons(db, skip=skip, limit=limit)
        logger.info(f"人物一覧取得完了: {len(persons)}件")
        return persons
    except Exception as e:
        logger.error(f"人物一覧取得エラー: {str(e)}")
        raise
```

### **2. サービスでのデバッグログ**

```python
# app/services/person_service.py
from ..core import get_logger

logger = get_logger("services.person")

def get_persons(self, db: Session, skip: int = 0, limit: int = 100):
    logger.debug(f"データベースクエリ実行: skip={skip}, limit={limit}")
    
    query = db.query(Person).offset(skip).limit(limit)
    logger.debug(f"SQLクエリ: {query}")
    
    result = query.all()
    logger.info(f"クエリ実行完了: {len(result)}件取得")
    
    return result
```

### **3. ミドルウェアでのデバッグログ**

```python
# app/middleware/logging.py
async def dispatch(self, request: Request, call_next: Callable) -> Response:
    self.logger.debug(f"リクエスト開始: {request.method} {request.url.path}")
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    self.logger.debug(f"リクエスト完了: {process_time:.3f}s")
    return response
```

### **4. 認証でのデバッグログ**

```python
# app/dependencies/auth.py
from ..core import get_logger

logger = get_logger("auth")

async def get_current_user(request: Request):
    logger.debug("認証処理開始")
    
    # 認証処理
    if api_key := request.headers.get("X-API-Key"):
        logger.debug(f"APIキー認証: {api_key[:8]}...")
        return verify_api_key(api_key)
    
    if auth_header := request.headers.get("Authorization"):
        logger.debug("JWT認証処理")
        return verify_jwt(auth_header)
    
    logger.warning("認証情報なし")
    raise HTTPException(status_code=401, detail="認証が必要です")
```

## 🔍 参考リンクの実装ポイント

### **1. [Apidog記事](https://apidog.com/jp/blog/version-2-logging-endpoints-with-python-fastapi/)のベストプラクティス**

#### **構造化ログの採用**
```python
# JSON形式でのログ出力
"json": {
    "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
    "datefmt": "%Y-%m-%d %H:%M:%S",
},
```

#### **ミドルウェアベースのリクエストログ**
```python
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # リクエスト開始・完了の自動ログ記録
        self.logger.info(f"受信リクエスト: {request.method} {request.url.path}")
        response = await call_next(request)
        self.logger.info(f"レスポンス完了: {request.method} {request.url.path} - Status: {response.status_code}")
        return response
```

### **2. 環境別設定の実装**

#### **開発環境**
```python
def setup_development_logging():
    os.environ["LOG_LEVEL"] = "DEBUG"
    setup_logging()
```

#### **本番環境**
```python
def setup_production_logging():
    os.environ["LOG_LEVEL"] = "INFO"
    setup_logging()
```

### **3. ローテーション機能**

```python
"file": {
    "class": "logging.handlers.RotatingFileHandler",
    "level": log_level,
    "formatter": "detailed",
    "filename": "logs/app.log",
    "maxBytes": 10485760,  # 10MB
    "backupCount": 5,       # 5世代保持
},
```

### **4. 階層化されたロガー設定**

```python
"loggers": {
    "app": {                    # アプリケーション全体
        "handlers": ["console", "file", "error_file"],
    },
    "app.middleware": {         # ミドルウェア専用
        "handlers": ["console", "file", "access_file"],
    },
    "app.auth": {              # 認証専用
        "handlers": ["console", "file", "error_file", "auth_file"],
    },
}
```

この実装により、FastAPIアプリケーションの動作を詳細に追跡し、問題の早期発見とパフォーマンス監視が可能になります。

## 🔍 参考リンクの実装ポイント
1. **[Apidog記事](https://apidog.com/jp/blog/
version-2-logging-endpoints-with-python-fastapi/)**のベストプラクティスを採用
2. **ミドルウェアベース**のリクエストログ記録
3. **構造化ログ**によるJSON形式出力
4. **環境別設定**による柔軟なログレベル制御
5. **ローテーション機能**によるログファイル管理