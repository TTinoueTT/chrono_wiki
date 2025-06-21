#!/bin/bash

# テスト用PostgreSQLコンテナを起動
echo "Starting test PostgreSQL container..."

psql ${TEST_DATABASE_URL} -c "\l"

psql ${TEST_DATABASE_URL} -c "\dt"

# テストを実行
echo "Running tests..."
python -m pytest tests/crud/ -v --tb=short


echo "Tests completed!"
