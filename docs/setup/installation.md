# インストール手順

このドキュメントでは、年表サービスAPIの開発環境構築について詳しく説明します。

## 📋 前提条件

### 必要なソフトウェア
- **Docker**: 20.10以上
- **Docker Compose**: 2.0以上
- **Git**: 2.30以上

### 推奨環境
- **OS**: Linux, macOS, Windows 10/11 (WSL2)
- **メモリ**: 8GB以上
- **ディスク**: 10GB以上の空き容量

## 🚀 クイックスタート

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd fast-api-try
```

### 2. 環境変数ファイルの設定
```bash
# .envファイルをコピー
cp .env.example .env

# 必要に応じて値を編集
nano .env
```

### 3. 開発環境の起動
```bash
# 開発環境を起動(ビルド対応)
docker compose -f docker-compose.dev.yml up --build -d

# サービスの起動のみ
docker compose -f docker-compose.dev.yml up -d
# テスト用 PostgreSQL の起動
docker compose -f docker-compose.dev.yml --profile test up -d
# カバレッジサービスを起動
docker compose -f docker-compose.dev.yml --profile coverage up -d


# ログを確認
docker compose -f docker-compose.dev.yml logs -f api
```

### 4. 動作確認
- **API ドキュメント**: http://localhost:8020/docs
- **ヘルスチェック**: http://localhost:8020/health

## 🐳 Docker環境の詳細

### 開発環境 (docker-compose.dev.yml)

#### サービス構成
```yaml
services:
  postgres:          # 本番用PostgreSQL
  test_postgres:     # テスト用PostgreSQL (profile: test)
  api:              # FastAPIアプリケーション
```

#### 本番用PostgreSQL
- **イメージ**: `postgres:17`
- **ポート**: `5432` (ホスト側)
- **用途**: 開発・本番データ
- **起動**: 通常の開発時は常時起動

#### テスト用PostgreSQL
- **イメージ**: `postgres:17`
- **ポート**: `5433` (ホスト側)
- **用途**: テスト専用データ
- **起動**: テスト実行時のみ起動（`--profile test`）

#### FastAPIアプリケーション
- **ポート**: `8020` (ホスト側)
- **ホットリロード**: 有効
- **デバッグモード**: 有効
- **ワーカー数**: 1（開発用）

### PostgreSQL 17の最適化設定

#### 開発環境での設定
```yaml
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

## 🧪 テスト環境の設定

### テスト用PostgreSQLの特徴
- **独立したデータベース**: 本番データに影響を与えない
- **自動クリーンアップ**: テスト終了時にコンテナを停止・削除
- **専用設定**: テスト用に最適化されたPostgreSQL設定
- **プロファイル制御**: `profiles: [test]`で通常起動時は無効

### テスト実行方法

#### 1. 自動実行（推奨）
```bash
# テスト用PostgreSQLを自動起動・停止
./run_tests.sh
```

#### 2. 手動実行
```bash
# テスト用PostgreSQLを起動
docker compose -f docker-compose.dev.yml --profile test up -d test_postgres

# テスト実行
python -m pytest tests/ -v

# テスト用PostgreSQLを停止
docker compose -f docker-compose.dev.yml --profile test down test_postgres
```

#### 3. 開発作業中の常時起動（オプション）
```bash
# 開発作業中にテスト用PostgreSQLも常時起動
docker compose -f docker-compose.dev.yml --profile test up -d

# 停止時
docker compose -f docker-compose.dev.yml --profile test down
```

### 開発作業中の常時起動について

**メリット**:
- テストの即座実行が可能
- データベース接続の確認が容易
- 開発フローがスムーズ

**デメリット**:
- リソース使用量の増加
- ポート競合の可能性（5433を使用）

**推奨設定**:
開発作業中は常時起動することを推奨します：

```bash
# 開発開始時
docker compose -f docker-compose.dev.yml --profile test up -d

# 開発終了時
docker compose -f docker-compose.dev.yml --profile test down
```

## 🔧 環境別の設定

### 開発環境 (docker-compose.dev.yml)
```yaml
# 特徴
- ホットリロード有効
- ソースコードのマウント
- デバッグモード有効
- ポート: 8020
- ワーカー数: 1
```

### ステージング環境 (docker-compose.stg.yml)
```yaml
# 特徴
- 本番に近い設定
- 2ワーカー
- デバッグモード無効
- ポート: 8030
```

### 本番環境 (docker-compose.prod.yml)
```yaml
# 特徴
- Gunicorn使用
- 4ワーカー
- デバッグモード無効
- ポート: 8040
```

## 🔍 動作確認

### 基本的な動作確認

#### 1. ヘルスチェック
```bash
curl http://localhost:8020/health
```

#### 2. API ドキュメント
- **Swagger UI**: http://localhost:8020/docs
- **ReDoc**: http://localhost:8020/redoc

#### 3. データベース接続確認
```bash
# PostgreSQLに接続
docker compose -f docker-compose.dev.yml exec postgres psql -h postgres -U chrono_wiki_user -d chrono_wiki

# テーブル一覧を確認
\dt
```

### テストの実行確認

#### 1. 単体テスト
```bash
# 全テスト実行
python -m pytest tests/ -v

# 特定のテストファイル
python -m pytest tests/test_api.py -v

# 特定のテストクラス
python -m pytest tests/test_api.py::TestAPI -v
```

#### 2. テストカバレッジ
```bash
# カバレッジ付きでテスト実行
python -m pytest tests/ --cov=app --cov-report=html

# カバレッジレポートを確認
open htmlcov/index.html
```

## 📚 参考資料

### 公式ドキュメント
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL 17 Documentation](https://www.postgresql.org/docs/17/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

### 関連リンク
- [設定ガイド](./configuration.md)
- [トラブルシューティング](./troubleshooting.md)
- [プロジェクトREADME](../../README.md)

---

**注意**: このドキュメントは開発環境の構築を目的としています。本番環境での使用には、セキュリティ設定やパフォーマンスチューニングが必要です。 