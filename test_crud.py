#!/usr/bin/env python3
"""
CRUD操作をテストするスクリプト
"""

from datetime import date

from app import crud, schemas
from app.database import SessionLocal, create_tables


def test_crud_operations():
    """CRUD操作をテスト"""
    print("=== CRUD操作テスト開始 ===")

    # テーブル作成確認
    create_tables()

    # データベースセッション取得
    db = SessionLocal()

    try:
        # 1. Person作成テスト
        print("\n1. Person作成テスト")
        person_data = schemas.PersonCreate(
            ssid="PERSON001",
            full_name="織田信長",
            display_name="信長",
            search_name="おだのぶなが",
            birth_date=date(1534, 6, 23),
            born_country="日本",
            born_region="尾張国",
            description="戦国時代の武将、天下統一を目指した",
            portrait_url="https://example.com/nobunaga.jpg",
        )

        person = crud.create_person(db, person_data)
        print(f"作成されたPerson: ID={person.id}, 名前={person.full_name}")

        # 2. Tag作成テスト
        print("\n2. Tag作成テスト")
        tag_data = schemas.TagCreate(
            ssid="TAG001",
            name="戦国武将",
            description="戦国時代の武将に関するタグ",
        )

        tag = crud.create_tag(db, tag_data)
        print(f"作成されたTag: ID={tag.id}, 名前={tag.name}")

        # 3. Event作成テスト
        print("\n3. Event作成テスト")
        event_data = schemas.EventCreate(
            ssid="EVENT001",
            title="桶狭間の戦い",
            start_data=date(1560, 5, 19),
            description="織田信長が今川義元を破った戦い",
            location_name="桶狭間",
            latitude=35.123456,
            longitude=136.789012,
        )

        event = crud.create_event(db, event_data)
        print(f"作成されたEvent: ID={event.id}, タイトル={event.title}")

        # 4. データ取得テスト
        print("\n4. データ取得テスト")

        # Person一覧取得
        persons = crud.get_persons(db, skip=0, limit=10)
        print(f"Person一覧: {len(persons)}件")
        for p in persons:
            print(f"  - {p.full_name} (ID: {p.id})")

        # SSIDでPerson取得
        person_by_ssid = crud.get_person_by_ssid(db, ssid="PERSON001")
        print(
            f"SSIDで取得したPerson: {person_by_ssid.full_name if person_by_ssid else 'Not found'}"
        )

        # Tag一覧取得
        tags = crud.get_tags(db, skip=0, limit=10)
        print(f"Tag一覧: {len(tags)}件")
        for t in tags:
            print(f"  - {t.name} (ID: {t.id})")

        # Event一覧取得
        events = crud.get_events(db, skip=0, limit=10)
        print(f"Event一覧: {len(events)}件")
        for e in events:
            print(f"  - {e.title} (ID: {e.id})")

        # 5. データ更新テスト
        print("\n5. データ更新テスト")
        update_data = schemas.PersonUpdate(
            full_name="織田信長（更新）",
            description="戦国時代の武将、天下統一を目指した（更新版）",
        )

        updated_person = crud.update_person(
            db, person_id=person.id, person=update_data
        )
        print(f"更新されたPerson: {updated_person.full_name}")

        # 6. データ削除テスト（最後に実行）
        print("\n6. データ削除テスト")
        success = crud.delete_person(db, person_id=person.id)
        print(f"Person削除: {'成功' if success else '失敗'}")

        success = crud.delete_tag(db, tag_id=tag.id)
        print(f"Tag削除: {'成功' if success else '失敗'}")

        success = crud.delete_event(db, event_id=event.id)
        print(f"Event削除: {'成功' if success else '失敗'}")

        print("\n=== CRUD操作テスト完了 ===")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    test_crud_operations()
