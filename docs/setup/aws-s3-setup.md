# AWS S3設定ガイド

このドキュメントでは、画像アップロード機能で使用するAWS S3の設定方法について説明します。

## 📋 前提条件

- AWSアカウント
- S3バケットの作成権限
- IAMユーザーの作成権限

## 🚀 セットアップ手順

### 1. S3バケットの作成

1. **AWS Management Console**にログイン
2. **S3サービス**に移動
3. **「バケットを作成」**をクリック
4. 以下の設定でバケットを作成：

```yaml
バケット名: your-app-images-bucket
リージョン: us-east-1 (推奨)
パブリックアクセス: ブロックしない
バケットのバージョニング: 無効
サーバーサイド暗号化: デフォルト
```

### 2. バケットポリシーの設定

以下のポリシーをバケットに適用して、画像ファイルの公開読み取りを許可します：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-app-images-bucket/*"
        }
    ]
}
```

### 3. CORS設定

バケットのCORS設定を追加して、Webアプリケーションからのアクセスを許可します：

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

### 4. IAMユーザーの作成

1. **IAMサービス**に移動
2. **「ユーザー」**→**「ユーザーを作成」**
3. ユーザー名: `s3-upload-user`
4. アクセスキーの作成: **プログラムによるアクセス**を選択

### 5. IAMポリシーの作成

以下のポリシーを作成してIAMユーザーにアタッチ：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-app-images-bucket",
                "arn:aws:s3:::your-app-images-bucket/*"
            ]
        }
    ]
}
```

## 🔧 環境変数の設定

`env.example`ファイルを参考に、以下の環境変数を設定してください：

```bash
# AWS S3設定
AWS_S3_BUCKET_NAME=your-app-images-bucket
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
```

### Docker Compose環境での設定

`docker-compose.dev.yml`の`api`サービスに環境変数を追加：

```yaml
services:
  api:
    environment:
      # ... 既存の環境変数 ...
      - AWS_S3_BUCKET_NAME=${AWS_S3_BUCKET_NAME}
      - AWS_REGION=${AWS_REGION}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
```

## 📁 ディレクトリ構造

S3バケット内の推奨ディレクトリ構造：

```
your-app-images-bucket/
├── avatars/           # ユーザーアバター画像
│   ├── user1.jpg
│   ├── user2.png
│   └── ...
├── events/            # イベント画像（将来の拡張用）
└── temp/              # 一時ファイル
```

## 🔒 セキュリティ考慮事項

### 1. アクセス制御
- **最小権限の原則**: 必要最小限の権限のみ付与
- **IAMロールの使用**: 可能であればIAMロールを使用
- **アクセスキーの定期ローテーション**: セキュリティ向上のため

### 2. ファイル制限
- **ファイルサイズ**: 最大5MB
- **ファイル形式**: JPG, JPEG, PNG, GIF, WebP
- **コンテンツ検証**: アップロード時の画像検証

### 3. コスト最適化
- **ライフサイクルポリシー**: 古いファイルの自動削除
- **ストレージクラス**: 適切なストレージクラスの選択
- **CDN統合**: CloudFrontとの統合でパフォーマンス向上

## 🧪 テスト

### 1. 接続テスト

```python
import boto3

# S3クライアントの初期化
s3_client = boto3.client(
    's3',
    region_name='us-east-1',
    aws_access_key_id='your-access-key',
    aws_secret_access_key='your-secret-key'
)

# バケットの存在確認
try:
    s3_client.head_bucket(Bucket='your-app-images-bucket')
    print("✅ S3バケットに正常に接続できました")
except Exception as e:
    print(f"❌ S3接続エラー: {e}")
```

### 2. アップロードテスト

```python
# テストファイルのアップロード
test_content = b'test file content'
s3_client.put_object(
    Bucket='your-app-images-bucket',
    Key='test/test.txt',
    Body=test_content
)
print("✅ テストファイルのアップロードが成功しました")
```

## 🚨 トラブルシューティング

### よくある問題

#### 1. 認証エラー
```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```

**解決方法**:
- 環境変数が正しく設定されているか確認
- AWS認証情報の有効性を確認

#### 2. アクセス拒否エラー
```
botocore.exceptions.ClientError: An error occurred (AccessDenied)
```

**解決方法**:
- IAMポリシーの権限を確認
- バケットポリシーの設定を確認

#### 3. バケットが見つからないエラー
```
botocore.exceptions.ClientError: An error occurred (NoSuchBucket)
```

**解決方法**:
- バケット名のスペルを確認
- リージョンの設定を確認

## 📚 参考リンク

- [AWS S3 ドキュメント](https://docs.aws.amazon.com/s3/)
- [boto3 ドキュメント](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [IAM ベストプラクティス](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

---

**注意**: 本番環境では、より厳密なセキュリティ設定を適用することを推奨します。 