#!/bin/bash

# モデル層とCRUD層のテスト実行スクリプト（コンテナ外から実行）

echo "🧪 モデル層とデータアクセス層のテストを実行中..."

# テスト用PostgreSQLコンテナを起動
echo "📦 テスト用PostgreSQLコンテナを起動中..."
docker compose -f docker-compose.dev.yml --profile test up -d test_postgres

# コンテナの起動を待つ
echo "⏳ PostgreSQLの起動を待機中..."
sleep 10

# テストコマンドを api コンテナ内で順次実行
echo "🔍 モデル層とCRUD層のテストを実行中..."

docker compose -f docker-compose.dev.yml --profile test exec api alembic upgrade head
docker compose -f docker-compose.dev.yml --profile test exec api bash -c 'DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m model -v --tb=short'
docker compose -f docker-compose.dev.yml --profile test exec api bash -c 'DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m crud -v --tb=short'
docker compose -f docker-compose.dev.yml --profile test exec api bash -c 'DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m service -v --tb=short'
docker compose -f docker-compose.dev.yml --profile test exec api bash -c 'DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m router -v --tb=short'
docker compose -f docker-compose.dev.yml --profile test exec api bash -c 'DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m health -v --tb=short'
docker compose -f docker-compose.dev.yml --profile test exec api bash -c 'DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m hybrid_auth -v --tb=short'
docker compose -f docker-compose.dev.yml --profile test exec api bash -c 'DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m batch -v --tb=short'
docker compose -f docker-compose.dev.yml --profile test exec api bash -c 'DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m integration -v --tb=short'
docker compose -f docker-compose.dev.yml --profile test exec api bash -c 'DATABASE_URL="$TEST_DATABASE_URL" python -m pytest --cov=app --cov-report=term-missing --cov-report=html -v --tb=short'

# テスト用コンテナを停止
echo "🛑 テスト用PostgreSQLコンテナを停止中..."
docker compose -f docker-compose.dev.yml --profile test down test_postgres

echo "✅ テスト完了！"
