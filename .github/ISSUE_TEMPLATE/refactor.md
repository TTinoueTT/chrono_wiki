---
name: ♻️ Refactoring
about: コードのリファクタリング提案やタスクを報告するときに使ってください
title: "[Refactor]"
labels: refactor
assignees: ''
---

## 概要（Summary）
<!-- 何をリファクタリングしたいのか、目的と対象を明確に記載してください -->

例：
- `UserService` クラスのメソッドが肥大化しているため分割したい
- 重複している `OrderController` のバリデーション処理を共通化したい

## 背景・動機（Motivation）
<!-- なぜ今リファクタリングが必要なのか、問題点や改善点を説明してください -->

例：
- 可読性・保守性が低下しているため
- パフォーマンス改善のため
- テストを書きやすくするため

## 実装イメージ（Implementation）
<!-- リファクタリング後のクラス構成やメソッド分割の案、サンプルコードなど具体的に -->

```php
// 例：UserService を細分化
- App\Services\UserService
+ App\Services\User\ProfileService
+ App\Services\User\AuthService
```

## 影響範囲（Impact）
<!-- リファクタリングに伴い影響を受ける画面・API・テストなどを列挙してください -->
- app/Http/Controllers/UserController.php
- tests/Feature/UserTest.php
- resources/views/user/*.blade.php

## チェックリスト（Checklist）
- [ ] 関数／メソッド単位でテストカバレッジを確認
- [ ] ドキュメント／README を必要に応じて更新
- [ ] 動作確認を実施（主要画面・API）

## 補足（Additional Context）
<!-- 参考リンクや過去の Issue、設計資料などがあれば貼ってください -->

