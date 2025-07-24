"""
人物ルーターの結合テスト

人物エンドポイントの統合テストを実装します。
実際のデータベースとサービスを使用してテストします。
"""

import uuid

import pytest
from fastapi import status

from app.enums.user_role import UserRole


@pytest.mark.router
@pytest.mark.integration
class TestPersonsRouter:
    """人物ルーターの結合テスト"""

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

    def test_create_person_success(self, client, sample_person_data):
        """人物作成の成功テスト（モデレーター権限）"""
        headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        response = client.post("/api/v1/persons/", json=sample_person_data, headers=headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["ssid"] == sample_person_data["ssid"]
        assert data["full_name"] == sample_person_data["full_name"]
        assert data["display_name"] == sample_person_data["display_name"]
        assert data["birth_date"] == sample_person_data["birth_date"]
        assert data["born_country"] == sample_person_data["born_country"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_person_duplicate_ssid(self, client, sample_person_data):
        """重複SSIDでの人物作成失敗テスト（モデレーター権限）"""
        headers = self._create_user_and_login(client, role=UserRole.MODERATOR)

        # 最初の作成
        response1 = client.post("/api/v1/persons/", json=sample_person_data, headers=headers)
        assert response1.status_code == status.HTTP_201_CREATED

        # 重複SSIDでの作成
        response2 = client.post("/api/v1/persons/", json=sample_person_data, headers=headers)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response2.json()["detail"]

    def test_create_person_missing_required_fields(self, client):
        """必須フィールド不足での人物作成失敗テスト（モデレーター権限）"""
        headers = self._create_user_and_login(client, role=UserRole.MODERATOR)

        invalid_data = {
            "ssid": "test_invalid",
            # full_name が不足
            "display_name": "テスト",
            "birth_date": "1534-06-23",
            "born_country": "日本",
        }

        response = client.post("/api/v1/persons/", json=invalid_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_person_invalid_date_range(self, client):
        """無効な日付範囲での人物作成失敗テスト（モデレーター権限）"""
        headers = self._create_user_and_login(client, role=UserRole.MODERATOR)

        invalid_data = {
            "ssid": "test_invalid_dates",
            "full_name": "無効な日付の人物",
            "display_name": "無効",
            "search_name": "むこうなにちづけのじんぶつ",
            "birth_date": "1582-06-21",  # 生年月日が没年月日より後
            "death_date": "1534-06-23",
            "born_country": "日本",
        }

        response = client.post("/api/v1/persons/", json=invalid_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Birth date cannot be after death date" in response.json()["detail"]

    def test_create_person_insufficient_permission(self, client, sample_person_data):
        """権限不足での人物作成失敗テスト（一般ユーザー）"""
        headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.post("/api/v1/persons/", json=sample_person_data, headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_persons_empty_list(self, client):
        """空の人物一覧取得テスト（一般ユーザー）"""
        headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.get("/api/v1/persons/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_persons_with_data(self, client, sample_person_data):
        """データありの人物一覧取得テスト（一般ユーザー）"""
        # モデレーターで人物を作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/persons/", json=sample_person_data, headers=moderator_headers)
        assert create_response.status_code == status.HTTP_201_CREATED

        # 一般ユーザーで一覧を取得
        user_headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.get("/api/v1/persons/", headers=user_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # 作成した人物が含まれていることを確認
        person_ids = [p["id"] for p in data]
        created_id = create_response.json()["id"]
        assert created_id in person_ids

    def test_get_persons_pagination(self, client):
        """人物一覧のページネーションテスト（一般ユーザー）"""
        # モデレーターで複数の人物を作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        for i in range(3):
            person_data = {
                "ssid": f"test_person_pag_{i}",
                "full_name": f"ページネーションテスト{i}",
                "display_name": f"ページ{i}",
                "search_name": f"ぺーじねーしょんてすと{i}",
                "birth_date": "1534-06-23",
                "born_country": "日本",
            }
            client.post("/api/v1/persons/", json=person_data, headers=moderator_headers)

        # 一般ユーザーでページネーション取得
        user_headers = self._create_user_and_login(client, role=UserRole.USER)

        # 最初の2件を取得
        response1 = client.get("/api/v1/persons/?skip=0&limit=2", headers=user_headers)
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        assert len(data1) <= 2

        # 次の2件を取得
        response2 = client.get("/api/v1/persons/?skip=2&limit=2", headers=user_headers)
        assert response2.status_code == status.HTTP_200_OK
        # データが取得できることを確認
        assert isinstance(response2.json(), list)

    def test_get_person_success(self, client, sample_person_data):
        """人物取得の成功テスト（一般ユーザー）"""
        # モデレーターで人物を作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/persons/", json=sample_person_data, headers=moderator_headers)
        created_person = create_response.json()

        # 一般ユーザーで人物を取得
        user_headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.get(f"/api/v1/persons/{created_person['id']}", headers=user_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == created_person["id"]
        assert data["ssid"] == sample_person_data["ssid"]
        assert data["full_name"] == sample_person_data["full_name"]

    def test_get_person_not_found(self, client):
        """存在しない人物の取得テスト（一般ユーザー）"""
        headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.get("/api/v1/persons/999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Person not found" in response.json()["detail"]

    def test_get_person_by_ssid_success(self, client, sample_person_data):
        """SSIDでの人物取得成功テスト（一般ユーザー）"""
        # モデレーターで人物を作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/persons/", json=sample_person_data, headers=moderator_headers)
        assert create_response.status_code == status.HTTP_201_CREATED

        # 一般ユーザーでSSID取得
        user_headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.get(f"/api/v1/persons/ssid/{sample_person_data['ssid']}", headers=user_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["ssid"] == sample_person_data["ssid"]
        assert data["full_name"] == sample_person_data["full_name"]

    def test_get_person_by_ssid_not_found(self, client):
        """存在しないSSIDでの人物取得テスト（一般ユーザー）"""
        headers = self._create_user_and_login(client, role=UserRole.USER)
        response = client.get("/api/v1/persons/ssid/non_existent_ssid", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Person not found" in response.json()["detail"]

    def test_update_person_success(self, client, sample_person_data):
        """人物更新の成功テスト（モデレーター権限）"""
        # モデレーターで人物を作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/persons/", json=sample_person_data, headers=moderator_headers)
        created_person = create_response.json()

        # 更新データ
        update_data = {
            "full_name": "更新後の名前",
            "description": "更新された説明",
        }

        # 人物を更新
        response = client.put(f"/api/v1/persons/{created_person['id']}", json=update_data, headers=moderator_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == created_person["id"]
        assert data["full_name"] == "更新後の名前"
        assert data["description"] == "更新された説明"
        assert data["ssid"] == sample_person_data["ssid"]  # 変更されていない

    def test_update_person_not_found(self, client):
        """存在しない人物の更新テスト（モデレーター権限）"""
        headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        update_data = {"full_name": "更新テスト"}

        response = client.put("/api/v1/persons/999", json=update_data, headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Person not found" in response.json()["detail"]

    def test_update_person_invalid_data(self, client, sample_person_data):
        """無効なデータでの人物更新テスト（モデレーター権限）"""
        # モデレーターで人物を作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/persons/", json=sample_person_data, headers=moderator_headers)
        created_person = create_response.json()

        # 無効な更新データ（生年月日が没年月日より後）
        invalid_update_data = {
            "birth_date": "1582-06-21",
            "death_date": "1534-06-23",
        }

        response = client.put(
            f"/api/v1/persons/{created_person['id']}", json=invalid_update_data, headers=moderator_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Birth date cannot be after death date" in response.json()["detail"]

    def test_update_person_insufficient_permission(self, client, sample_person_data):
        """権限不足での人物更新失敗テスト（一般ユーザー）"""
        # モデレーターで人物を作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/persons/", json=sample_person_data, headers=moderator_headers)
        created_person = create_response.json()

        # 一般ユーザーで更新を試行
        user_headers = self._create_user_and_login(client, role=UserRole.USER)
        update_data = {"full_name": "権限不足テスト"}
        response = client.put(f"/api/v1/persons/{created_person['id']}", json=update_data, headers=user_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_person_success(self, client, sample_person_data):
        """人物削除の成功テスト（管理者権限）"""
        # モデレーターで人物を作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/persons/", json=sample_person_data, headers=moderator_headers)
        created_person = create_response.json()

        # 管理者で人物を削除
        admin_headers = self._create_user_and_login(client, role=UserRole.ADMIN)
        response = client.delete(f"/api/v1/persons/{created_person['id']}", headers=admin_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 削除確認
        get_response = client.get(f"/api/v1/persons/{created_person['id']}", headers=admin_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_person_not_found(self, client):
        """存在しない人物の削除テスト（管理者権限）"""
        headers = self._create_user_and_login(client, role=UserRole.ADMIN)
        response = client.delete("/api/v1/persons/999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Person not found" in response.json()["detail"]

    def test_delete_person_insufficient_permission(self, client, sample_person_data):
        """権限不足での人物削除失敗テスト（モデレーター）"""
        # モデレーターで人物を作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        create_response = client.post("/api/v1/persons/", json=sample_person_data, headers=moderator_headers)
        created_person = create_response.json()

        # モデレーターで削除を試行（管理者権限が必要）
        response = client.delete(f"/api/v1/persons/{created_person['id']}", headers=moderator_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_person_crud_workflow(self, client):
        """人物CRUD操作の完全なワークフローテスト"""
        # 1. モデレーターで人物を作成
        moderator_headers = self._create_user_and_login(client, role=UserRole.MODERATOR)
        person_data = {
            "ssid": "test_workflow_001",
            "full_name": "ワークフローテスト",
            "display_name": "ワークフロー",
            "search_name": "わーくふろーてすと",
            "birth_date": "1534-06-23",
            "born_country": "日本",
            "description": "ワークフローテスト用の人物",
        }

        create_response = client.post("/api/v1/persons/", json=person_data, headers=moderator_headers)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_person = create_response.json()

        # 2. 一般ユーザーで作成した人物を取得
        user_headers = self._create_user_and_login(client, role=UserRole.USER)
        get_response = client.get(f"/api/v1/persons/{created_person['id']}", headers=user_headers)
        assert get_response.status_code == status.HTTP_200_OK
        retrieved_person = get_response.json()
        assert retrieved_person["ssid"] == person_data["ssid"]

        # 3. 一般ユーザーでSSIDで人物を取得
        ssid_response = client.get(f"/api/v1/persons/ssid/{person_data['ssid']}", headers=user_headers)
        assert ssid_response.status_code == status.HTTP_200_OK
        ssid_person = ssid_response.json()
        assert ssid_person["id"] == created_person["id"]

        # 4. モデレーターで人物を更新
        update_data = {
            "full_name": "更新されたワークフロー",
            "description": "更新された説明",
        }
        update_response = client.put(
            f"/api/v1/persons/{created_person['id']}", json=update_data, headers=moderator_headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        updated_person = update_response.json()
        assert updated_person["full_name"] == "更新されたワークフロー"

        # 5. 一般ユーザーで一覧に含まれていることを確認
        list_response = client.get("/api/v1/persons/", headers=user_headers)
        assert list_response.status_code == status.HTTP_200_OK
        persons = list_response.json()
        person_ids = [p["id"] for p in persons]
        assert created_person["id"] in person_ids

        # 6. 管理者で人物を削除
        admin_headers = self._create_user_and_login(client, role=UserRole.ADMIN)
        delete_response = client.delete(f"/api/v1/persons/{created_person['id']}", headers=admin_headers)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # 7. 削除確認
        final_get_response = client.get(f"/api/v1/persons/{created_person['id']}", headers=admin_headers)
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND
