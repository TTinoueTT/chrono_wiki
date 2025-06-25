#!/bin/bash

# テスト用PostgreSQLコンテナを起動
echo "Starting test PostgreSQL container..."
docker-compose -f docker-compose.dev.yml --profile test up -d test_postgres

# コンテナの起動を待つ
echo "Waiting for PostgreSQL to be ready..."
sleep 10

# テストを実行
echo "Running tests..."
python -m pytest tests/crud/ -v --tb=short

# テスト用コンテナを停止
echo "Stopping test PostgreSQL container..."
docker-compose -f docker-compose.dev.yml --profile test down test_postgres

echo "Tests completed!"
