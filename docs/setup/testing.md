
```bash
python -m pytest tests/services/test_s3_storage_service.py::TestS3StorageService::test_s3_connection -v -s

```

このコマンドの解説：

**各要素の意味：**

1. **`python -m pytest`**: Pythonのモジュールとしてpytestを実行

2. **`tests/services/test_s3_storage_service.py`**: 実行対象のテストファイルパス

3. **`::TestS3StorageService`**: テストクラス名を指定（`::`で区切る）

4. **`::test_s3_connection`**: 特定のテストメソッド名を指定

5. **`-v`**: verbose（詳細）モード。テストの詳細情報を表示

6. **`-s`**: 標準出力をキャプチャしない。`print()`文の出力が表示される

**実行されるテスト：**
- `tests/services/test_s3_storage_service.py`ファイル内の
- `TestS3StorageService`クラスの
- `test_s3_connection`メソッドのみを実行

**用途：**
- 特定のテストのみを実行したい場合
- デバッグ時に特定のテストに集中したい場合
- S3接続テストのみを確認したい場合

ただし、現在のファイル構造では`test_s3_storage_service.py`ファイルが存在しないため、このコマンドは失敗する可能性があります。