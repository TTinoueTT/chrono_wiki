#!/bin/bash

# テスト用PostgreSQLコンテナを起動
echo "Starting test PostgreSQL container..."

psql "${TEST_DATABASE_URL}" -c "\l"

psql "${TEST_DATABASE_URL}" -c "\dt"

# テストを実行
echo "Running tests..."

echo "Running model tests..."
python -m pytest -m model -v --tb=short

echo "Running crud tests..."
python -m pytest -m crud -v --tb=short

echo "Running service tests..."
python -m pytest -m service -v --tb=short

echo "Running router tests..."
python -m pytest -m router -v --tb=short

echo "Running integration tests..."
python -m pytest -m integration -v --tb=short

echo "Running all tests with coverage..."
python -m pytest --cov=app --cov-report=term-missing --cov-report=html -v --tb=short

echo "Tests completed!"
