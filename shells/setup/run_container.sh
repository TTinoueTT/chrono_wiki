#!/bin/bash
# 開発環境を起動(ビルド対応)
docker compose -f docker-compose.dev.yml up --build -d

# サービスの起動のみ
docker-compose -f docker-compose.dev.yml up -d
# テスト用 PostgreSQL の起動
docker-compose -f docker-compose.dev.yml --profile test up -d
# カバレッジサービスを起動
docker-compose -f docker-compose.dev.yml --profile coverage up -d
