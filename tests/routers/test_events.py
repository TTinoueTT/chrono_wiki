"""
イベントルーターの結合テスト

イベントエンドポイントの統合テストを実装します。
実際のデータベースとサービスを使用してテストします。
"""

import uuid

import pytest
from fastapi import status

from app.enums.user_role import UserRole


@pytest.mark.router
@pytest.mark.integration
class TestEventsRouter:
    """イベントルーターの結合テスト"""

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

    def test_create_event_success(self, client, sample_event_data):
        """イベント作成の成功テスト（モデレーター権限）"""
        headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        response = client.post("/api/v1/events/", json=sample_event_data, headers=headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["ssid"] == sample_event_data["ssid"]
        assert data["title"] == sample_event_data["title"]
        assert data["start_date"] == sample_event_data["start_date"]
        assert data["location_name"] == sample_event_data["location_name"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_event_duplicate_ssid(self, client, sample_event_data):
        """重複SSIDでのイベント作成失敗テスト（モデレーター権限）"""
        headers = self._create_user_and_login(client, role=UserRole.MODERATOR)

        # 最初の作成
        response1 = client.post("/api/v1/events/", json=sample_event_data, headers=headers)
        assert response1.status_code == status.HTTP_201_CREATED

        # 重複SSIDでの作成
        response2 = client.post("/api/v1/events/", json=sample_event_data, headers=headers)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response2.json()["detail"]

    def test_create_event_missing_required_fields(self, client):
        """必須フィールド不足でのイベント作成失敗テスト（モデレーター権限）"""
        headers = self._create_user_and_login(client, role=UserRole.MODERATOR)

        invalid_data = {
            "ssid": "test_invalid",
            # title が不足
            "start_date": "1560-05-19",
            "location_name": "桶狭間",
        }

        response = client.post("/api/v1/events/", json=invalid_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_event_invalid_date_range(self, client):
        """無効な日付範囲でのイベント作成失敗テスト（モデレーター権限）"""
        headers = self._create_user_and_login(client, role=UserRole.MODERATOR)

        invalid_data = {
            "ssid": "test_invalid_dates",
            "title": "無効な日付のイベント",
            "start_date": "1560-05-20",  # 開始日が終了日より後
            "end_date": "1560-05-19",
            "location_name": "桶狭間",
        }

        response = client.post("/api/v1/events/", json=invalid_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Start date cannot be after end date" in response.json()["detail"]

    def test_create_event_insufficient_permission(self, client, sample_event_data):
        """権限不足でのイベント作成失敗テスト（一般ユーザー）"""
        headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.post("/api/v1/events/", json=sample_event_data, headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_events_empty_list(self, client):
        """空のイベント一覧取得テスト（一般ユーザー）"""
        headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.get("/api/v1/events/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_events_with_data(self, client, sample_event_data):
        """データありのイベント一覧取得テスト（一般ユーザー）"""
        # モデレーターでイベントを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/events/", json=sample_event_data, headers=moderator_headers)
        assert create_response.status_code == status.HTTP_201_CREATED

        # 一般ユーザーで一覧を取得
        user_headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.get("/api/v1/events/", headers=user_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # 作成したイベントが含まれていることを確認
        event_ids = [e["id"] for e in data]
        created_id = create_response.json()["id"]
        assert created_id in event_ids

    def test_get_events_pagination(self, client):
        """イベント一覧のページネーションテスト（一般ユーザー）"""
        # モデレーターで複数のイベントを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        for i in range(3):
            event_data = {
                "ssid": f"test_event_pag_{i}",
                "title": f"ページネーションテスト{i}",
                "start_date": "1560-05-19",
                "location_name": f"場所{i}",
            }
            client.post("/api/v1/events/", json=event_data, headers=moderator_headers)

        # 一般ユーザーでページネーション取得
        user_headers = self._create_user_and_login(client, role=UserRole.USER)

        # 最初の2件を取得
        response1 = client.get("/api/v1/events/?skip=0&limit=2", headers=user_headers)
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        assert len(data1) <= 2

        # 次の2件を取得
        response2 = client.get("/api/v1/events/?skip=2&limit=2", headers=user_headers)
        assert response2.status_code == status.HTTP_200_OK
        # データが取得できることを確認
        assert isinstance(response2.json(), list)

    def test_get_event_success(self, client, sample_event_data):
        """イベント取得の成功テスト（一般ユーザー）"""
        # モデレーターでイベントを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/events/", json=sample_event_data, headers=moderator_headers)
        created_event = create_response.json()

        # 一般ユーザーでイベントを取得
        user_headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.get(f"/api/v1/events/{created_event['id']}", headers=user_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == created_event["id"]
        assert data["ssid"] == sample_event_data["ssid"]
        assert data["title"] == sample_event_data["title"]

    def test_get_event_not_found(self, client):
        """存在しないイベントの取得テスト（一般ユーザー）"""
        headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.get("/api/v1/events/999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Event not found" in response.json()["detail"]

    def test_update_event_success(self, client, sample_event_data):
        """イベント更新の成功テスト（モデレーター権限）"""
        # モデレーターでイベントを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/events/", json=sample_event_data, headers=moderator_headers)
        created_event = create_response.json()

        # 更新データ
        update_data = {
            "title": "更新されたタイトル",
            "description": "更新された説明",
        }

        # イベントを更新
        response = client.put(f"/api/v1/events/{created_event['id']}", json=update_data, headers=moderator_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == created_event["id"]
        assert data["title"] == "更新されたタイトル"
        assert data["description"] == "更新された説明"
        assert data["ssid"] == sample_event_data["ssid"]  # 変更されていない

    def test_update_event_not_found(self, client):
        """存在しないイベントの更新テスト（モデレーター権限）"""
        headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        update_data = {"title": "更新テスト"}

        response = client.put("/api/v1/events/999", json=update_data, headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Event not found" in response.json()["detail"]

    def test_update_event_invalid_data(self, client, sample_event_data):
        """無効なデータでのイベント更新テスト（モデレーター権限）"""
        # モデレーターでイベントを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/events/", json=sample_event_data, headers=moderator_headers)
        created_event = create_response.json()

        # 無効な更新データ（開始日が終了日より後）
        invalid_update_data = {
            "start_date": "1560-05-20",
            "end_date": "1560-05-19",
        }

        response = client.put(
            f"/api/v1/events/{created_event['id']}", json=invalid_update_data, headers=moderator_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Start date cannot be after end date" in response.json()["detail"]

    def test_update_event_insufficient_permission(self, client, sample_event_data):
        """権限不足でのイベント更新失敗テスト（一般ユーザー）"""
        # モデレーターでイベントを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/events/", json=sample_event_data, headers=moderator_headers)
        created_event = create_response.json()

        # 一般ユーザーで更新を試行
        user_headers = self._create_user_and_login(client, role=UserRole.USER)
        update_data = {"title": "権限不足テスト"}
        response = client.put(f"/api/v1/events/{created_event['id']}", json=update_data, headers=user_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_event_success(self, client, sample_event_data):
        """イベント削除の成功テスト（管理者権限）"""
        # モデレーターでイベントを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/events/", json=sample_event_data, headers=moderator_headers)
        created_event = create_response.json()

        # 管理者でイベントを削除
        admin_headers = self._create_user_and_login(client, role=UserRole.ADMIN)
        response = client.delete(f"/api/v1/events/{created_event['id']}", headers=admin_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 削除確認
        get_response = client.get(f"/api/v1/events/{created_event['id']}", headers=admin_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_event_not_found(self, client):
        """存在しないイベントの削除テスト（管理者権限）"""
        headers = self._create_user_and_login(client, role=UserRole.ADMIN)
        response = client.delete("/api/v1/events/999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Event not found" in response.json()["detail"]

    def test_delete_event_insufficient_permission(self, client, sample_event_data):
        """権限不足でのイベント削除失敗テスト（モデレーター）"""
        # モデレーターでイベントを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/events/", json=sample_event_data, headers=moderator_headers)
        created_event = create_response.json()

        # モデレーターで削除を試行（管理者権限が必要）
        response = client.delete(f"/api/v1/events/{created_event['id']}", headers=moderator_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_event_crud_workflow(self, client):
        """イベントCRUD操作の完全なワークフローテスト"""
        # 1. モデレーターでイベントを作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        event_data = {
            "ssid": "test_workflow_001",
            "title": "ワークフローテスト",
            "start_date": "1560-05-19",
            "end_date": "1560-05-19",
            "description": "ワークフローテスト用のイベント",
            "location_name": "桶狭間",
            "latitude": 35.0,
            "longitude": 137.0,
        }

        create_response = client.post("/api/v1/events/", json=event_data, headers=moderator_headers)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_event = create_response.json()

        # 2. 一般ユーザーで作成したイベントを取得
        user_headers = self._create_user_and_login(client, role=UserRole.USER)
        get_response = client.get(f"/api/v1/events/{created_event['id']}", headers=user_headers)
        assert get_response.status_code == status.HTTP_200_OK
        retrieved_event = get_response.json()
        assert retrieved_event["ssid"] == event_data["ssid"]

        # 3. モデレーターでイベントを更新
        update_data = {
            "title": "更新されたワークフロー",
            "description": "更新された説明",
        }
        update_response = client.put(
            f"/api/v1/events/{created_event['id']}", json=update_data, headers=moderator_headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        updated_event = update_response.json()
        assert updated_event["title"] == "更新されたワークフロー"

        # 4. 一般ユーザーで一覧に含まれていることを確認
        list_response = client.get("/api/v1/events/", headers=user_headers)
        assert list_response.status_code == status.HTTP_200_OK
        events = list_response.json()
        event_ids = [e["id"] for e in events]
        assert created_event["id"] in event_ids

        # 5. 管理者でイベントを削除
        admin_headers = self._create_user_and_login(client, role=UserRole.ADMIN)
        delete_response = client.delete(f"/api/v1/events/{created_event['id']}", headers=admin_headers)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # 6. 削除確認
        final_get_response = client.get(f"/api/v1/events/{created_event['id']}", headers=admin_headers)
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND
