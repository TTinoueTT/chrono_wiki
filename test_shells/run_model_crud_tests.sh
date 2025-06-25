#!/bin/bash

# モデル層とCRUD層のテスト実行スクリプト

echo "🧪 モデル層とデータアクセス層のテストを実行中..."

# テスト用PostgreSQLコンテナを起動
echo "📦 テスト用PostgreSQLコンテナを起動中..."
docker-compose -f docker-compose.dev.yml --profile test up -d test_postgres

# コンテナの起動を待つ
echo "⏳ PostgreSQLの起動を待機中..."
sleep 10

# モデル層とCRUD層のテストを実行
echo "🔍 モデル層とCRUD層のテストを実行中..."
python -m pytest tests/models/ tests/crud/ -v --tb=short --cov=app.models --cov=app.crud --cov-report=term-missing

# テスト用コンテナを停止
echo "🛑 テスト用PostgreSQLコンテナを停止中..."
docker-compose -f docker-compose.dev.yml --profile test down test_postgres

echo "✅ テスト完了！" 