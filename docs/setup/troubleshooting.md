# トラブルシューティング

このドキュメントでは、年表サービスAPIの環境構築や運用中に発生する可能性のある問題とその解決方法について説明します。

## 🛠️ よくある問題と解決方法

### 1. ポートが既に使用されている

#### 症状
```bash
Error: Port 8020 is already in use
```

#### 解決方法
```bash
# 使用中のポートを確認
netstat -tulpn | grep :8020

# プロセスを終了
sudo kill -9 <PID>

# または、別のポートを使用
# .envファイルでAPI_PORTを変更
```

#### 予防策
- 開発開始前にポートの使用状況を確認
- 複数のプロジェクトで異なるポートを使用

### 2. データベース接続エラー

#### 症状
```bash
Connection refused
psycopg2.OperationalError: could not connect to server
```

#### 解決方法
```bash
# PostgreSQLコンテナの状態確認
docker compose -f docker-compose.dev.yml ps

# ログを確認
docker compose -f docker-compose.dev.yml logs postgres

# コンテナを再起動
docker compose -f docker-compose.dev.yml restart postgres

# データベース接続テスト
docker compose -f docker-compose.dev.yml exec postgres psql -U chrono_wiki_user -d chrono_wiki -c "SELECT 1;"
```

#### 予防策
- ヘルスチェックの設定
- 適切な依存関係の設定
- 環境変数の確認

### 3. メモリ不足

#### 症状
```bash
Out of memory
Cannot allocate memory
```

#### 解決方法
```bash
# Dockerのメモリ制限を確認
docker system df

# 未使用リソースを削除
docker system prune -a

# Docker Desktopのメモリ設定を増加
# Docker Desktop > Settings > Resources > Memory
```

#### 予防策
- 定期的なDockerクリーンアップ
- 適切なメモリ設定
- 不要なコンテナの停止

### 4. 権限エラー

#### 症状
```bash
Permission denied
Cannot connect to the Docker daemon
```

#### 解決方法
```bash
# Dockerグループにユーザーを追加
sudo usermod -aG docker $USER

# 再ログイン
newgrp docker

# または、sudoを使用
sudo docker compose -f docker-compose.dev.yml up -d
```

#### 予防策
- 適切なユーザー権限の設定
- Dockerグループへの追加

### 5. 環境変数が読み込まれない

#### 症状
```bash
Environment variable not found
```

#### 解決方法
```bash
# .envファイルの存在確認
ls -la .env

# 環境変数の確認
docker compose -f docker-compose.dev.yml config

# 手動で環境変数を設定
export POSTGRES_DB=chrono_wiki
```

#### 予防策
- .envファイルの作成確認
- 環境変数の命名規則の統一
- 設定ファイルの検証

### 6. テスト用PostgreSQLの起動エラー

#### 症状
```bash
Profile "test" not found
```

#### 解決方法
```bash
# 正しいプロファイル指定
docker compose -f docker-compose.dev.yml --profile test up -d test_postgres

# プロファイルの確認
docker compose -f docker-compose.dev.yml config --profiles
```

#### 予防策
- プロファイルの正しい指定
- docker-compose.ymlファイルの確認

## 📋 ログの確認方法

### アプリケーションログ
```bash
# リアルタイムログ
docker compose -f docker-compose.dev.yml logs -f api

# 特定の行数
docker compose -f docker-compose.dev.yml logs --tail=100 api

# 特定の時間以降
docker compose -f docker-compose.dev.yml logs --since="2024-01-01T00:00:00" api
```

### データベースログ
```bash
# PostgreSQLログ
docker compose -f docker-compose.dev.yml logs postgres

# テスト用PostgreSQLログ
docker compose -f docker-compose.dev.yml logs test_postgres

# データベース接続確認
docker compose -f docker-compose.dev.yml exec postgres pg_isready -U chrono_wiki_user -d chrono_wiki
```

### コンテナの状態確認
```bash
# 全コンテナの状態
docker compose -f docker-compose.dev.yml ps

# 特定のコンテナの詳細
docker compose -f docker-compose.dev.yml ps api

# コンテナのリソース使用量
docker stats
```

## 🔍 デバッグ手順

### 1. 基本的なデバッグ手順
```bash
# 1. コンテナの状態確認
docker compose -f docker-compose.dev.yml ps

# 2. ログの確認
docker compose -f docker-compose.dev.yml logs api

# 3. 環境変数の確認
docker compose -f docker-compose.dev.yml config

# 4. ネットワーク接続の確認
docker compose -f docker-compose.dev.yml exec api ping postgres
```

### 2. データベースデバッグ
```bash
# データベース接続テスト
docker compose -f docker-compose.dev.yml exec postgres psql -U chrono_wiki_user -d chrono_wiki -c "SELECT version();"

# テーブル一覧確認
docker compose -f docker-compose.dev.yml exec postgres psql -U chrono_wiki_user -d chrono_wiki -c "\dt"

# 接続数確認
docker compose -f docker-compose.dev.yml exec postgres psql -U chrono_wiki_user -d chrono_wiki -c "SELECT count(*) FROM pg_stat_activity;"
```

### 3. アプリケーションデバッグ
```bash
# コンテナ内でのデバッグ
docker compose -f docker-compose.dev.yml exec api bash

# Pythonプロセスの確認
docker compose -f docker-compose.dev.yml exec api ps aux

# ポートの確認
docker compose -f docker-compose.dev.yml exec api netstat -tulpn
```

## 🚨 緊急時の対応

### 1. サービスが起動しない場合
```bash
# 全サービスを停止
docker compose -f docker-compose.dev.yml down

# ボリュームを削除（データが消える）
docker compose -f docker-compose.dev.yml down -v

# イメージを再ビルド
docker compose -f docker-compose.dev.yml build --no-cache

# サービスを再起動
docker compose -f docker-compose.dev.yml up -d
```

### 2. データベースが破損した場合
```bash
# データベースのバックアップ（事前に作成）
docker compose -f docker-compose.dev.yml exec postgres pg_dump -U chrono_wiki_user chrono_wiki > backup.sql

# データベースの復元
docker compose -f docker-compose.dev.yml exec postgres psql -U chrono_wiki_user -d chrono_wiki < backup.sql
```

### 3. ディスク容量不足
```bash
# Dockerの使用量確認
docker system df

# 未使用リソースの削除
docker system prune -a

# 特定のリソースの削除
docker volume prune
docker image prune
docker container prune
```

## 📊 パフォーマンス問題

### 1. メモリ使用量の最適化
```bash
# メモリ使用量の確認
docker stats

# PostgreSQLのメモリ設定調整
# docker-compose.dev.ymlのshared_buffersを調整
```

### 2. ディスクI/Oの最適化
```bash
# ディスク使用量の確認
df -h

# Dockerボリュームの確認
docker volume ls
```

### 3. ネットワークの最適化
```bash
# ネットワーク接続の確認
docker network ls
docker network inspect fast-api-try_default
```

## 🔧 設定の検証

### 1. 環境変数の検証
```bash
# 環境変数の確認
docker compose -f docker-compose.dev.yml config

# 特定の環境変数を確認
echo $POSTGRES_DB
echo $API_PORT
```

### 2. 設定ファイルの検証
```bash
# Docker Compose設定の検証
docker compose -f docker-compose.dev.yml config --quiet

# 環境変数ファイルの確認
cat .env | grep -v '^#' | grep -v '^$'
```

### 3. 依存関係の検証
```bash
# 依存関係の確認
docker compose -f docker-compose.dev.yml config --services

# ヘルスチェックの確認
docker compose -f docker-compose.dev.yml ps
```

## 📞 サポート

### 問題報告時の情報
問題を報告する際は、以下の情報を含めてください：

1. **エラーメッセージ**: 完全なエラーメッセージ
2. **環境情報**: OS、Dockerバージョン、Pythonバージョン
3. **実行コマンド**: 実行したコマンド
4. **ログ**: 関連するログファイル
5. **設定ファイル**: 環境変数や設定ファイルの内容

### サポートチャンネル
- **GitHub Issues**: バグ報告・機能要望
- **ドキュメント**: このドキュメントの確認
- **ログ確認**: エラーログの詳細確認

## 🔗 関連リンク

- [インストール手順](./installation.md)
- [設定ガイド](./configuration.md)
- [プロジェクトREADME](../../README.md)

---

**注意**: 本番環境での問題解決には、より慎重なアプローチが必要です。データのバックアップを必ず取得してから作業を行ってください。 