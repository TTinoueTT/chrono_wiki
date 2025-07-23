#!/bin/bash

# テスト用PostgreSQLコンテナを起動
echo "Starting test PostgreSQL container..."

psql "${TEST_DATABASE_URL}" -c "\l"

psql "${TEST_DATABASE_URL}" -c "\dt"

# テストを実行
echo "Running tests..."

echo "Running model tests..."
DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m model -v --tb=short

echo "Running crud tests..."
DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m crud -v --tb=short

echo "Running service tests..."
DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m service -v --tb=short

echo "Running router tests..."
DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m router -v --tb=short

echo "Running health tests..."
DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m health -v --tb=short

echo "Running hybrid auth tests (by mark)..."
DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m hybrid_auth -v --tb=short

echo "Running batch tests (by mark)..."
DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m batch -v --tb=short

echo "Running integration tests..."
DATABASE_URL="$TEST_DATABASE_URL" python -m pytest -m integration -v --tb=short

echo "Running all tests with coverage..."
DATABASE_URL="$TEST_DATABASE_URL" python -m pytest --cov=app --cov-report=term-missing --cov-report=html -v --tb=short

echo "Tests completed!"
