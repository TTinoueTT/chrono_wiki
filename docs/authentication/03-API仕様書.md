# 03. API仕様書

## 📋 概要

このドキュメントでは、歴史的年表APIの認証・認可エンドポイントの詳細仕様を定義します。

## 🔐 認証エンドポイント

### 1. ユーザー登録

**エンドポイント**: `POST /auth/register`

**説明**: 新しいユーザーアカウントを作成します。

**リクエスト**:
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword123",
  "full_name": "John Doe",
  "is_active": true,
  "role": "user"
}
```

**レスポンス** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "username",
  "full_name": "John Doe",
  "is_active": true,
  "role": "user",
  "avatar_url": null,
  "bio": null,
  "last_login": null,
  "failed_login_attempts": "0",
  "locked_until": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**エラーレスポンス**:
- `400 Bad Request`: メールアドレスまたはユーザー名が重複
- `422 Unprocessable Entity`: バリデーションエラー

### 2. ログイン

**エンドポイント**: `POST /auth/login`

**説明**: OAuth2パスワードフローによるログイン

**リクエスト** (Form Data):
```
username: user@example.com
password: securepassword123
```

**レスポンス** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**エラーレスポンス**:
- `401 Unauthorized`: 認証情報が間違っている
- `423 Locked`: アカウントがロックされている
- `400 Bad Request`: ユーザーが非アクティブ

### 3. トークン更新

**エンドポイント**: `POST /auth/refresh`

**説明**: リフレッシュトークンを使用してアクセストークンを更新

**リクエスト**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**レスポンス** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**エラーレスポンス**:
- `401 Unauthorized`: リフレッシュトークンが無効

### 4. 現在のユーザー情報取得

**エンドポイント**: `GET /auth/me`

**説明**: 現在ログインしているユーザーの情報を取得

**認証**: 必須

**レスポンス** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "username",
  "full_name": "John Doe",
  "is_active": true,
  "role": "user",
  "avatar_url": "https://example.com/avatar.jpg",
  "bio": "Software Developer",
  "last_login": "2024-01-01T12:00:00Z",
  "failed_login_attempts": "0",
  "locked_until": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**エラーレスポンス**:
- `401 Unauthorized`: 認証されていない

### 5. ユーザー情報更新

**エンドポイント**: `PUT /auth/me`

**説明**: 現在のユーザー情報を更新

**認証**: 必須

**リクエスト**:
```json
{
  "full_name": "Updated Name",
  "bio": "Updated bio",
  "avatar_url": "https://example.com/new-avatar.jpg"
}
```

**レスポンス** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "username",
  "full_name": "Updated Name",
  "is_active": true,
  "role": "user",
  "avatar_url": "https://example.com/new-avatar.jpg",
  "bio": "Updated bio",
  "last_login": "2024-01-01T12:00:00Z",
  "failed_login_attempts": "0",
  "locked_until": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:30:00Z"
}
```

### 6. パスワード変更

**エンドポイント**: `POST /auth/change-password`

**説明**: 現在のパスワードを変更

**認証**: 必須

**リクエスト** (Query Parameters):
```
current_password: oldpassword123
new_password: newpassword123
```

**レスポンス** (200 OK):
```json
{
  "message": "Password changed successfully"
}
```

**エラーレスポンス**:
- `400 Bad Request`: 現在のパスワードが間違っている
- `401 Unauthorized`: 認証されていない
- `422 Unprocessable Entity`: 新しいパスワードが短すぎる

### 7. ログアウト

**エンドポイント**: `POST /auth/logout`

**説明**: ユーザーをログアウト

**認証**: 必須

**レスポンス** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

## 👥 ユーザー管理エンドポイント

### 1. ユーザー一覧取得

**エンドポイント**: `GET /users/`

**説明**: ユーザー一覧を取得（管理者のみ）

**認証**: 管理者権限必須

**クエリパラメータ**:
- `skip`: スキップ数（デフォルト: 0）
- `limit`: 取得件数（デフォルト: 100）

**レスポンス** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "username": "username",
    "full_name": "John Doe",
    "is_active": true,
    "role": "user",
    "avatar_url": null,
    "bio": null,
    "last_login": "2024-01-01T12:00:00Z",
    "failed_login_attempts": "0",
    "locked_until": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### 2. アクティブユーザー一覧取得

**エンドポイント**: `GET /users/active`

**説明**: アクティブユーザー一覧を取得（モデレーター以上）

**認証**: モデレーター権限必須

**クエリパラメータ**:
- `skip`: スキップ数（デフォルト: 0）
- `limit`: 取得件数（デフォルト: 100）

**レスポンス** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "username": "username",
    "full_name": "John Doe",
    "is_active": true,
    "role": "user",
    "avatar_url": null,
    "bio": null,
    "last_login": "2024-01-01T12:00:00Z",
    "failed_login_attempts": "0",
    "locked_until": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### 3. 役割別ユーザー一覧取得

**エンドポイント**: `GET /users/role/{role}`

**説明**: 指定された役割のユーザー一覧を取得（モデレーター以上）

**認証**: モデレーター権限必須

**パスパラメータ**:
- `role`: ユーザー役割（user, moderator, admin）

**クエリパラメータ**:
- `skip`: スキップ数（デフォルト: 0）
- `limit`: 取得件数（デフォルト: 100）

**レスポンス** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "admin@example.com",
    "username": "adminuser",
    "full_name": "Admin User",
    "is_active": true,
    "role": "admin",
    "avatar_url": null,
    "bio": null,
    "last_login": "2024-01-01T12:00:00Z",
    "failed_login_attempts": "0",
    "locked_until": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### 4. ユーザー詳細取得

**エンドポイント**: `GET /users/{user_id}`

**説明**: 指定されたユーザーの詳細情報を取得（自分自身または管理者のみ）

**認証**: 必須（自分自身または管理者）

**パスパラメータ**:
- `user_id`: ユーザーID

**レスポンス** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "username",
  "full_name": "John Doe",
  "is_active": true,
  "role": "user",
  "avatar_url": null,
  "bio": null,
  "last_login": "2024-01-01T12:00:00Z",
  "failed_login_attempts": "0",
  "locked_until": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**エラーレスポンス**:
- `404 Not Found`: ユーザーが見つからない
- `403 Forbidden`: 権限不足

### 5. ユーザー更新

**エンドポイント**: `PUT /users/{user_id}`

**説明**: 指定されたユーザーを更新（自分自身または管理者のみ）

**認証**: 必須（自分自身または管理者）

**パスパラメータ**:
- `user_id`: ユーザーID

**リクエスト**:
```json
{
  "full_name": "Updated Name",
  "bio": "Updated bio",
  "role": "moderator"
}
```

**レスポンス** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "username",
  "full_name": "Updated Name",
  "is_active": true,
  "role": "moderator",
  "avatar_url": null,
  "bio": "Updated bio",
  "last_login": "2024-01-01T12:00:00Z",
  "failed_login_attempts": "0",
  "locked_until": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:30:00Z"
}
```

### 6. ユーザー削除

**エンドポイント**: `DELETE /users/{user_id}`

**説明**: 指定されたユーザーを削除（管理者のみ）

**認証**: 管理者権限必須

**パスパラメータ**:
- `user_id`: ユーザーID

**レスポンス** (204 No Content)

**エラーレスポンス**:
- `404 Not Found`: ユーザーが見つからない

### 7. ユーザー有効化

**エンドポイント**: `POST /users/{user_id}/activate`

**説明**: 指定されたユーザーを有効化（管理者のみ）

**認証**: 管理者権限必須

**パスパラメータ**:
- `user_id`: ユーザーID

**レスポンス** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "username",
  "full_name": "John Doe",
  "is_active": true,
  "role": "user",
  "avatar_url": null,
  "bio": null,
  "last_login": "2024-01-01T12:00:00Z",
  "failed_login_attempts": "0",
  "locked_until": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:30:00Z"
}
```

### 8. ユーザー無効化

**エンドポイント**: `POST /users/{user_id}/deactivate`

**説明**: 指定されたユーザーを無効化（管理者のみ）

**認証**: 管理者権限必須

**パスパラメータ**:
- `user_id`: ユーザーID

**レスポンス** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "username",
  "full_name": "John Doe",
  "is_active": false,
  "role": "user",
  "avatar_url": null,
  "bio": null,
  "last_login": "2024-01-01T12:00:00Z",
  "failed_login_attempts": "0",
  "locked_until": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:30:00Z"
}
```

### 9. ユーザーアカウントロック

**エンドポイント**: `POST /users/{user_id}/lock`

**説明**: 指定されたユーザーアカウントをロック（管理者のみ）

**認証**: 管理者権限必須

**パスパラメータ**:
- `user_id`: ユーザーID

**クエリパラメータ**:
- `lock_minutes`: ロック時間（分）（デフォルト: 30）

**レスポンス** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "username",
  "full_name": "John Doe",
  "is_active": true,
  "role": "user",
  "avatar_url": null,
  "bio": null,
  "last_login": "2024-01-01T12:00:00Z",
  "failed_login_attempts": "5",
  "locked_until": "2024-01-01T13:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:30:00Z"
}
```

### 10. ユーザーアカウントロック解除

**エンドポイント**: `POST /users/{user_id}/unlock`

**説明**: 指定されたユーザーアカウントのロックを解除（管理者のみ）

**認証**: 管理者権限必須

**パスパラメータ**:
- `user_id`: ユーザーID

**レスポンス** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "username",
  "full_name": "John Doe",
  "is_active": true,
  "role": "user",
  "avatar_url": null,
  "bio": null,
  "last_login": "2024-01-01T12:00:00Z",
  "failed_login_attempts": "0",
  "locked_until": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:30:00Z"
}
```

## 📊 統計・分析エンドポイント

### 1. ユーザー統計取得

**エンドポイント**: `GET /users/stats/count`

**説明**: ユーザー統計情報を取得（モデレーター以上）

**認証**: モデレーター権限必須

**レスポンス** (200 OK):
```json
{
  "total_users": 100,
  "active_users": 85,
  "inactive_users": 15
}
```

### 2. 役割別ユーザー数取得

**エンドポイント**: `GET /users/stats/role/{role}/count`

**説明**: 指定された役割のユーザー数を取得（モデレーター以上）

**認証**: モデレーター権限必須

**パスパラメータ**:
- `role`: ユーザー役割（user, moderator, admin）

**レスポンス** (200 OK):
```json
{
  "role": "user",
  "count": 80
}
```

## 🔐 認証方式

### 1. JWT認証
- **アルゴリズム**: HS256
- **有効期限**: アクセストークン30分、リフレッシュトークン7日
- **ペイロード**: ユーザーID、メール、ロール、発行時刻

### 2. APIキー認証
- **ヘッダー**: `X-API-Key`
- **用途**: システム間通信、バッチ処理
- **設定**: 環境変数`API_KEY`

### 3. OAuth2パスワードフロー
- **グラントタイプ**: password
- **スコープ**: read, write, admin
- **リフレッシュ**: 自動トークン更新

## 📝 エラーレスポンス

### 共通エラーフォーマット

```json
{
  "detail": "エラーメッセージ",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### HTTPステータスコード

| ステータスコード | 説明 | 使用例 |
|---------------|------|--------|
| 200 | OK | 正常なレスポンス |
| 201 | Created | ユーザー登録成功 |
| 204 | No Content | ユーザー削除成功 |
| 400 | Bad Request | バリデーションエラー |
| 401 | Unauthorized | 認証失敗 |
| 403 | Forbidden | 権限不足 |
| 404 | Not Found | リソースが見つからない |
| 422 | Unprocessable Entity | リクエスト形式エラー |
| 423 | Locked | アカウントロック |

## 🔗 関連ドキュメント

- [01. 認証システム概要](./01-認証システム概要.md)
- [02. データベース設計](./02-データベース設計.md)
- [04. シーケンス図](./04-シーケンス図.md)
- [05. 実装ガイド](./05-実装ガイド.md) 