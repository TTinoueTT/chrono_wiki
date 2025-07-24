# ドキュメント

このディレクトリには、年表サービスAPIの詳細なドキュメントが含まれています。

## 📁 ドキュメント構造

```
docs/
├── README.md              # このファイル（ドキュメント概要）
├── setup/                 # 環境構築関連
│   ├── installation.md    # インストール手順
│   ├── configuration.md   # 設定ガイド
│   └── troubleshooting.md # トラブルシューティング
├── api/                   # API関連
│   ├── overview.md        # API概要
│   ├── endpoints.md       # エンドポイント詳細
│   └── examples.md        # API使用例
├── development/           # 開発関連
│   ├── architecture.md    # アーキテクチャ説明
│   ├── coding-standards.md # コーディング規約
│   └── testing.md         # テストガイド
├── deployment/            # デプロイ関連
│   ├── production.md      # 本番環境デプロイ
│   └── monitoring.md      # 監視・ログ
└── database/              # データベース関連
    ├── schema.md          # スキーマ設計
    └── migrations.md      # マイグレーション
```

## 🚀 クイックリンク

### 環境構築
- **[インストール手順](./setup/installation.md)**: 開発環境の構築手順
- **[設定ガイド](./setup/configuration.md)**: 環境変数と設定ファイルの説明
- **[トラブルシューティング](./setup/troubleshooting.md)**: よくある問題と解決方法

### API開発
- **[API概要](./api/overview.md)**: APIの全体像と設計思想
- **[エンドポイント詳細](./api/endpoints.md)**: 各エンドポイントの仕様
- **[API使用例](./api/examples.md)**: 実際の使用例とサンプルコード

### 開発ガイド
- **[アーキテクチャ説明](./development/architecture.md)**: システムアーキテクチャの詳細
- **[コーディング規約](./development/coding-standards.md)**: 開発時のコーディング規約
- **[テストガイド](./development/testing.md)**: テストの書き方と実行方法

### デプロイ・運用
- **[本番環境デプロイ](./deployment/production.md)**: 本番環境へのデプロイ手順
- **[監視・ログ](./deployment/monitoring.md)**: 監視設定とログ管理

### データベース
- **[スキーマ設計](./database/schema.md)**: データベーススキーマの詳細
- **[マイグレーション](./database/migrations.md)**: データベースマイグレーションの管理

## 📝 ドキュメントの更新

### ドキュメント更新のルール
1. **新機能追加時**: 関連するドキュメントを必ず更新
2. **API変更時**: エンドポイントドキュメントを更新
3. **設定変更時**: 設定ガイドを更新
4. **バグ修正時**: トラブルシューティングを更新

### ドキュメントの書き方
- **Markdown形式**: 統一性を保つためMarkdownを使用
- **日本語**: 基本的に日本語で記述
- **コード例**: 実際に動作するコード例を含める
- **図表**: 必要に応じて図表を使用して説明

## 🔗 外部リンク

- **[プロジェクトREADME](../README.md)**: プロジェクトの概要
- **[GitHub Issues](https://github.com/your-repo/issues)**: バグ報告・機能要望
- **[API ドキュメント](http://localhost:8020/docs)**: 自動生成されたAPI仕様書

---

**注意**: このドキュメントは継続的に更新されます。最新の情報については、各セクションのドキュメントを参照してください。 