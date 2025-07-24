"""
タグルーターの結合テスト

タグエンドポイントの統合テストを実装します。
実際のデータベースとサービスを使用してテストします。
"""

import uuid

import pytest
from fastapi import status

from app.enums.user_role import UserRole


@pytest.mark.router
@pytest.mark.integration
class TestTagsRouter:
    """タグルーターの結合テスト"""

    def _create_user_and_login(self, client, role: UserRole = UserRole.USER):
        """ユーザーを作成してログインし、JWTトークンを取得"""
        user_data = {
            "email": f"test_{uuid.uuid4()}@example.com",
            "username": f"testuser_{uuid.uuid4()}",
            "password": "testpassword123",
            "full_name": f"Test User ({role.value})",
            "role": role.value,
        }
        client.post("/api/v1/auth/register", json=user_data)

        login_data = {"username": user_data["email"], "password": "testpassword123"}
        login_response = client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        token_data = login_response.json()
        return {"Authorization": f"Bearer {token_data['access_token']}"}

    def test_create_tag_success(self, client, sample_tag_data):
        """タグ作成の成功テスト（モデレーター権限）"""
        headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        response = client.post("/api/v1/tags/", json=sample_tag_data, headers=headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["ssid"] == sample_tag_data["ssid"]
        assert data["name"] == sample_tag_data["name"]
        assert data["description"] == sample_tag_data["description"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_tag_duplicate_ssid(self, client, sample_tag_data):
        """重複SSIDでのタグ作成失敗テスト（モデレーター権限）"""
        headers = self._create_user_and_login(client, role=UserRole.MODERATOR)

        # 最初の作成
        response1 = client.post("/api/v1/tags/", json=sample_tag_data, headers=headers)
        assert response1.status_code == status.HTTP_201_CREATED

        # 重複SSIDでの作成
        response2 = client.post("/api/v1/tags/", json=sample_tag_data, headers=headers)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response2.json()["detail"]

    def test_create_tag_missing_required_fields(self, client):
        """必須フィールド不足でのタグ作成失敗テスト（モデレーター権限）"""
        headers = self._create_user_and_login(client, role=UserRole.MODERATOR)

        invalid_data = {
            "ssid": "test_invalid",
            # name が不足
            "description": "テスト用のタグ",
        }

        response = client.post("/api/v1/tags/", json=invalid_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_tag_insufficient_permission(self, client, sample_tag_data):
        """権限不足でのタグ作成失敗テスト（一般ユーザー）"""
        headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.post("/api/v1/tags/", json=sample_tag_data, headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_tags_empty_list(self, client):
        """空のタグ一覧取得テスト（一般ユーザー）"""
        headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.get("/api/v1/tags/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_tags_with_data(self, client, sample_tag_data):
        """データありのタグ一覧取得テスト（一般ユーザー）"""
        # モデレーターでタグを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/tags/", json=sample_tag_data, headers=moderator_headers)
        assert create_response.status_code == status.HTTP_201_CREATED

        # 一般ユーザーで一覧を取得
        user_headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.get("/api/v1/tags/", headers=user_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # 作成したタグが含まれていることを確認
        tag_ids = [t["id"] for t in data]
        created_id = create_response.json()["id"]
        assert created_id in tag_ids

    def test_get_tags_pagination(self, client):
        """タグ一覧のページネーションテスト（一般ユーザー）"""
        # モデレーターで複数のタグを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        for i in range(3):
            tag_data = {
                "ssid": f"test_tag_pag_{i}",
                "name": f"ページネーションテスト{i}",
                "description": f"テスト用タグ{i}",
            }
            client.post("/api/v1/tags/", json=tag_data, headers=moderator_headers)

        # 一般ユーザーでページネーション取得
        user_headers = self._create_user_and_login(client, role=UserRole.USER)

        # 最初の2件を取得
        response1 = client.get("/api/v1/tags/?skip=0&limit=2", headers=user_headers)
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        assert len(data1) <= 2

        # 次の2件を取得
        response2 = client.get("/api/v1/tags/?skip=2&limit=2", headers=user_headers)
        assert response2.status_code == status.HTTP_200_OK
        # データが取得できることを確認
        assert isinstance(response2.json(), list)

    def test_get_tag_success(self, client, sample_tag_data):
        """タグ取得の成功テスト（一般ユーザー）"""
        # モデレーターでタグを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/tags/", json=sample_tag_data, headers=moderator_headers)
        created_tag = create_response.json()

        # 一般ユーザーでタグを取得
        user_headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.get(f"/api/v1/tags/{created_tag['id']}", headers=user_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == created_tag["id"]
        assert data["ssid"] == sample_tag_data["ssid"]
        assert data["name"] == sample_tag_data["name"]

    def test_get_tag_not_found(self, client):
        """存在しないタグの取得テスト（一般ユーザー）"""
        headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.get("/api/v1/tags/999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Tag not found" in response.json()["detail"]

    def test_update_tag_success(self, client, sample_tag_data):
        """タグ更新の成功テスト（モデレーター権限）"""
        # モデレーターでタグを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/tags/", json=sample_tag_data, headers=moderator_headers)
        created_tag = create_response.json()

        # 更新データ
        update_data = {
            "name": "更新されたタグ名",
            "description": "更新された説明",
        }

        # タグを更新
        response = client.put(f"/api/v1/tags/{created_tag['id']}", json=update_data, headers=moderator_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == created_tag["id"]
        assert data["name"] == "更新されたタグ名"
        assert data["description"] == "更新された説明"
        assert data["ssid"] == sample_tag_data["ssid"]  # 変更されていない

    def test_update_tag_not_found(self, client):
        """存在しないタグの更新テスト（モデレーター権限）"""
        headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        update_data = {"name": "更新テスト"}

        response = client.put("/api/v1/tags/999", json=update_data, headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Tag not found" in response.json()["detail"]

    def test_update_tag_invalid_data(self, client, sample_tag_data):
        """無効なデータでのタグ更新テスト（モデレーター権限）"""
        # モデレーターでタグを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/tags/", json=sample_tag_data, headers=moderator_headers)
        created_tag = create_response.json()

        # 無効な更新データ（名前が長すぎる）
        invalid_update_data = {
            "name": "a" * 51,  # 51文字（制限超過）
        }

        response = client.put(f"/api/v1/tags/{created_tag['id']}", json=invalid_update_data, headers=moderator_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_tag_insufficient_permission(self, client, sample_tag_data):
        """権限不足でのタグ更新失敗テスト（一般ユーザー）"""
        # モデレーターでタグを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/tags/", json=sample_tag_data, headers=moderator_headers)
        created_tag = create_response.json()

        # 一般ユーザーで更新を試行
        user_headers = self._create_user_and_login(client, role=UserRole.USER)
        update_data = {"name": "権限不足テスト"}
        response = client.put(f"/api/v1/tags/{created_tag['id']}", json=update_data, headers=user_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_tag_success(self, client, sample_tag_data):
        """タグ削除の成功テスト（管理者権限）"""
        # モデレーターでタグを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/tags/", json=sample_tag_data, headers=moderator_headers)
        created_tag = create_response.json()

        # 管理者でタグを削除
        admin_headers = self._create_user_and_login(client, role=UserRole.ADMIN)
        response = client.delete(f"/api/v1/tags/{created_tag['id']}", headers=admin_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 削除確認
        get_response = client.get(f"/api/v1/tags/{created_tag['id']}", headers=admin_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_tag_not_found(self, client):
        """存在しないタグの削除テスト（管理者権限）"""
        headers = self._create_user_and_login(client, role=UserRole.ADMIN)
        response = client.delete("/api/v1/tags/999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Tag not found" in response.json()["detail"]

    def test_delete_tag_insufficient_permission(self, client, sample_tag_data):
        """権限不足でのタグ削除失敗テスト（モデレーター）"""
        # モデレーターでタグを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/tags/", json=sample_tag_data, headers=moderator_headers)
        created_tag = create_response.json()

        # モデレーターで削除を試行（管理者権限が必要）
        response = client.delete(f"/api/v1/tags/{created_tag['id']}", headers=moderator_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_tag_crud_workflow(self, client):
        """タグCRUD操作の完全なワークフローテスト"""
        # 1. モデレーターでタグを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        tag_data = {
            "ssid": "test_workflow_001",
            "name": "ワークフローテスト",
            "description": "ワークフローテスト用のタグ",
        }

        create_response = client.post("/api/v1/tags/", json=tag_data, headers=moderator_headers)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_tag = create_response.json()

        # 2. 一般ユーザーで作成したタグを取得
        user_headers = self._create_user_and_login(client, role=UserRole.USER)
        get_response = client.get(f"/api/v1/tags/{created_tag['id']}", headers=user_headers)
        assert get_response.status_code == status.HTTP_200_OK
        retrieved_tag = get_response.json()
        assert retrieved_tag["ssid"] == tag_data["ssid"]

        # 3. モデレーターでタグを更新
        update_data = {
            "name": "更新されたワークフロー",
            "description": "更新された説明",
        }
        update_response = client.put(f"/api/v1/tags/{created_tag['id']}", json=update_data, headers=moderator_headers)
        assert update_response.status_code == status.HTTP_200_OK
        updated_tag = update_response.json()
        assert updated_tag["name"] == "更新されたワークフロー"

        # 4. 一般ユーザーで一覧に含まれていることを確認
        list_response = client.get("/api/v1/tags/", headers=user_headers)
        assert list_response.status_code == status.HTTP_200_OK
        tags = list_response.json()
        tag_ids = [t["id"] for t in tags]
        assert created_tag["id"] in tag_ids

        # 5. 管理者でタグを削除
        admin_headers = self._create_user_and_login(client, role=UserRole.ADMIN)
        delete_response = client.delete(f"/api/v1/tags/{created_tag['id']}", headers=admin_headers)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # 6. 削除確認
        final_get_response = client.get(f"/api/v1/tags/{created_tag['id']}", headers=admin_headers)
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND
