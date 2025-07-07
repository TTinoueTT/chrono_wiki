参考リンクを確認して、FastAPIでのログ設定を実装します。まず、現在のlogsディレクトリの状況を確認します。

Ran tool
logsディレクトリが既に存在し、ログファイルも作成されていることを確認しました。参考リンクの内容を基に、FastAPI用のログ設定を実装します。

## 1. ログ設定ファイルの作成

## 2. coreパッケージの初期化ファイル作成

## 3. リクエストログミドルウェアの作成

## 4. main.pyにログ設定を追加

Read file: app/main.py
## 5. デモコードの作成

## 6. main.pyにデモルーターを追加

## 7. テスト用のログ設定を追加

## ログ設定の実装完了

参考リンクの内容に基づいて、FastAPI用の包括的なログ設定を実装しました。

### 📁 実装したファイル構成

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

### 🔧 ログ設定の特徴

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

### 🚀 デモエンドポイント

以下のエンドポイントでログ機能をテストできます：

#### 基本ログデモ
```bash
curl http://localhost:8000/api/v1/demo/logging
```

#### 認証ログデモ
```bash
curl http://localhost:8000/api/v1/demo/auth-logging
```

#### サービスログデモ
```bash
curl http://localhost:8000/api/v1/demo/service-logging
```

#### エラーログデモ
```bash
curl http://localhost:8000/api/v1/demo/error-logging
```

#### リクエスト情報デモ
```bash
curl http://localhost:8000/api/v1/demo/request-info
```

#### パフォーマンスログデモ
```bash
curl http://localhost:8000/api/v1/demo/performance-logging
```

#### 構造化ログデモ
```bash
curl http://localhost:8000/api/v1/demo/structured-logging
```

### 📊 ログ出力例

#### アプリケーションログ (`logs/app.log`)
```
2024-01-15 10:30:00 - app.main - INFO - FastAPI application initialized
2024-01-15 10:30:05 - app.routers.demo - INFO - ログデモエンドポイントが呼び出されました
2024-01-15 10:30:05 - app.routers.demo - INFO - これはINFOレベルのログです
```

#### アクセスログ (`logs/access.log`)
```json
{"timestamp": "2024-01-15 10:30:05", "level": "INFO", "logger": "app.middleware.logging", "message": "受信リクエスト: GET /api/v1/demo/logging - IP: 127.0.0.1 - User-Agent: curl/7.68.0"}
```

#### エラーログ (`logs/error.log`)
```
2024-01-15 10:30:10 - app.routers.demo - ERROR - エラーログデモ: ゼロ除算エラーが発生しました: division by zero
```

### 🔍 参考リンクの実装ポイント

1. **[Apidog記事](https://apidog.com/jp/blog/version-2-logging-endpoints-with-python-fastapi/)**のベストプラクティスを採用
2. **ミドルウェアベース**のリクエストログ記録
3. **構造化ログ**によるJSON形式出力
4. **環境別設定**による柔軟なログレベル制御
5. **ローテーション機能**によるログファイル管理

この実装により、FastAPIアプリケーションの動作を詳細に追跡し、問題の早期発見とパフォーマンス監視が可能になります。