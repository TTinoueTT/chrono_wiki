"""
データベースシーディングスクリプト

歴史的人物、イベント、タグ、ユーザーのサンプルデータをデータベースに投入します。
"""

from datetime import date
from typing import List

from sqlalchemy.orm import Session

from . import models, schemas
from .crud import EventCRUD, PersonCRUD, TagCRUD
from .crud.user import user_crud
from .database import SessionLocal
from .enums import EventPersonRole, UserRole
from .models.user import User


def seed_persons(db: Session) -> List[models.Person]:
    """人物データをシード"""
    person_crud = PersonCRUD()

    persons_data = [
        {
            "ssid": "oda_nobunaga",
            "full_name": "織田信長",
            "display_name": "織田信長",
            "birth_date": date(1534, 6, 23),
            "death_date": date(1582, 6, 21),
            "born_country": "日本",
            "born_region": "尾張国",
            "description": "戦国時代の武将。天下統一を目指した戦国大名。",
        },
        {
            "ssid": "toyotomi_hideyoshi",
            "full_name": "豊臣秀吉",
            "display_name": "豊臣秀吉",
            "birth_date": date(1537, 3, 17),
            "death_date": date(1598, 9, 18),
            "born_country": "日本",
            "born_region": "尾張国",
            "description": "織田信長の家臣から天下人となった武将。",
        },
        {
            "ssid": "tokugawa_ieyasu",
            "full_name": "徳川家康",
            "display_name": "徳川家康",
            "birth_date": date(1543, 1, 31),
            "death_date": date(1616, 6, 1),
            "born_country": "日本",
            "born_region": "三河国",
            "description": "江戸幕府を開いた初代将軍。",
        },
        {
            "ssid": "napoleon_bonaparte",
            "full_name": "ナポレオン・ボナパルト",
            "display_name": "ナポレオン・ボナパルト",
            "birth_date": date(1769, 8, 15),
            "death_date": date(1821, 5, 5),
            "born_country": "フランス",
            "born_region": "コルシカ島",
            "description": "フランスの軍人・政治家。フランス第一帝政の皇帝。",
        },
        {
            "ssid": "abraham_lincoln",
            "full_name": "エイブラハム・リンカーン",
            "display_name": "エイブラハム・リンカーン",
            "birth_date": date(1809, 2, 12),
            "death_date": date(1865, 4, 15),
            "born_country": "アメリカ合衆国",
            "born_region": "ケンタッキー州",
            "description": "アメリカ合衆国第16代大統領。奴隷制廃止を推進。",
        },
    ]

    created_persons = []
    for person_data in persons_data:
        try:
            person = person_crud.create(db, obj_in=schemas.PersonCreate(**person_data))  # type: ignore
            created_persons.append(person)
            print(f"✓ 人物を作成: {person.full_name}")
        except Exception as e:
            print(f"✗ 人物作成失敗: {person_data['full_name']} - {e}")

    return created_persons


def seed_tags(db: Session) -> List[models.Tag]:
    """タグデータをシード"""
    tag_crud = TagCRUD()

    tags_data = [
        {
            "ssid": "sengoku_period",
            "name": "戦国時代",
            "description": "日本の戦国時代に関するタグ",
        },
        {
            "ssid": "edo_period",
            "name": "江戸時代",
            "description": "日本の江戸時代に関するタグ",
        },
        {
            "ssid": "french_revolution",
            "name": "フランス革命",
            "description": "フランス革命に関するタグ",
        },
        {
            "ssid": "american_civil_war",
            "name": "南北戦争",
            "description": "アメリカ南北戦争に関するタグ",
        },
        {
            "ssid": "military_leader",
            "name": "軍事指導者",
            "description": "軍事指導者に関するタグ",
        },
        {
            "ssid": "politician",
            "name": "政治家",
            "description": "政治家に関するタグ",
        },
        {
            "ssid": "emperor",
            "name": "皇帝",
            "description": "皇帝に関するタグ",
        },
        {
            "ssid": "president",
            "name": "大統領",
            "description": "大統領に関するタグ",
        },
    ]

    created_tags = []
    for tag_data in tags_data:
        try:
            tag = tag_crud.create(db, obj_in=schemas.TagCreate(**tag_data))
            created_tags.append(tag)
            print(f"✓ タグを作成: {tag.name}")
        except Exception as e:
            print(f"✗ タグ作成失敗: {tag_data['name']} - {e}")

    return created_tags


def seed_events(db: Session) -> List[models.Event]:
    """イベントデータをシード"""
    event_crud = EventCRUD()

    events_data = [
        {
            "ssid": "battle_of_okehazama",
            "title": "桶狭間の戦い",
            "start_date": date(1560, 5, 19),
            "end_date": date(1560, 5, 19),
            "description": "織田信長が今川義元を破った戦い。少数の軍勢で大軍を破った奇襲戦として有名。",
            "location_name": "桶狭間",
            "latitude": 35.0,
            "longitude": 137.0,
        },
        {
            "ssid": "honnoji_incident",
            "title": "本能寺の変",
            "start_date": date(1582, 6, 21),
            "end_date": date(1582, 6, 21),
            "description": "明智光秀が織田信長を襲撃した事件。信長は自害した。",
            "location_name": "本能寺",
            "latitude": 35.0,
            "longitude": 135.8,
        },
        {
            "ssid": "battle_of_sekigahara",
            "title": "関ヶ原の戦い",
            "start_date": date(1600, 10, 21),
            "end_date": date(1600, 10, 21),
            "description": "徳川家康率いる東軍と石田三成率いる西軍の戦い。家康が勝利し、天下統一を決定づけた。",
            "location_name": "関ヶ原",
            "latitude": 35.4,
            "longitude": 136.5,
        },
        {
            "ssid": "french_revolution_start",
            "title": "フランス革命開始",
            "start_date": date(1789, 7, 14),
            "end_date": date(1789, 7, 14),
            "description": "バスティーユ牢獄の襲撃によりフランス革命が開始された。",
            "location_name": "パリ",
            "latitude": 48.9,
            "longitude": 2.3,
        },
        {
            "ssid": "napoleon_crowned_emperor",
            "title": "ナポレオン戴冠式",
            "start_date": date(1804, 12, 2),
            "end_date": date(1804, 12, 2),
            "description": "ナポレオン・ボナパルトがフランス皇帝として戴冠した。",
            "location_name": "ノートルダム大聖堂",
            "latitude": 48.9,
            "longitude": 2.3,
        },
        {
            "ssid": "battle_of_waterloo",
            "title": "ワーテルローの戦い",
            "start_date": date(1815, 6, 18),
            "end_date": date(1815, 6, 18),
            "description": "ナポレオンがイギリス・プロイセン連合軍に敗れた戦い。",
            "location_name": "ワーテルロー",
            "latitude": 50.7,
            "longitude": 4.4,
        },
        {
            "ssid": "american_civil_war_start",
            "title": "南北戦争開始",
            "start_date": date(1861, 4, 12),
            "end_date": date(1861, 4, 12),
            "description": "サムター要塞への攻撃により南北戦争が開始された。",
            "location_name": "サムター要塞",
            "latitude": 32.7,
            "longitude": -79.9,
        },
        {
            "ssid": "lincoln_assassination",
            "title": "リンカーン暗殺",
            "start_date": date(1865, 4, 14),
            "end_date": date(1865, 4, 15),
            "description": "エイブラハム・リンカーンがジョン・ウィルクス・ブースに暗殺された。",
            "location_name": "フォード劇場",
            "latitude": 38.9,
            "longitude": -77.0,
        },
    ]

    created_events = []
    for event_data in events_data:
        try:
            event = event_crud.create(db, obj_in=schemas.EventCreate(**event_data))  # type: ignore
            created_events.append(event)
            print(f"✓ イベントを作成: {event.title}")
        except Exception as e:
            print(f"✗ イベント作成失敗: {event_data['title']} - {e}")

    return created_events


def seed_person_tags(db: Session, persons: List[models.Person], tags: List[models.Tag]):
    """人物とタグの関連をシード"""
    print("\n🔗 人物-タグ関連をシード中...")

    # 人物とタグのマッピング
    person_tag_mappings = [
        # 織田信長
        ("oda_nobunaga", ["sengoku_period", "military_leader"]),
        # 豊臣秀吉
        ("toyotomi_hideyoshi", ["sengoku_period", "military_leader", "politician"]),
        # 徳川家康
        ("tokugawa_ieyasu", ["sengoku_period", "edo_period", "military_leader", "politician"]),
        # ナポレオン
        ("napoleon_bonaparte", ["french_revolution", "military_leader", "politician", "emperor"]),
        # リンカーン
        ("abraham_lincoln", ["american_civil_war", "politician", "president"]),
    ]

    # SSIDからIDへのマッピングを作成
    person_map = {p.ssid: p.id for p in persons}  # type: ignore
    tag_map = {t.ssid: t.id for t in tags}  # type: ignore

    created_relations = 0
    for person_ssid, tag_ssids in person_tag_mappings:
        person_id = person_map.get(person_ssid)  # type: ignore
        if not person_id:  # type: ignore
            print(f"⚠️ 人物が見つかりません: {person_ssid}")
            continue

        for tag_ssid in tag_ssids:
            tag_id = tag_map.get(tag_ssid)  # type: ignore
            if not tag_id:  # type: ignore
                print(f"⚠️ タグが見つかりません: {tag_ssid}")
                continue

            try:
                # 中間テーブルにレコードを追加
                person_tag = models.PersonTag(person_id=person_id, tag_id=tag_id)
                db.add(person_tag)
                created_relations += 1
                print(f"✓ 関連を作成: {person_ssid} - {tag_ssid}")
            except Exception as e:
                print(f"✗ 関連作成失敗: {person_ssid} - {tag_ssid} - {e}")

    db.commit()
    print(f"✅ 人物-タグ関連: {created_relations}件作成")


def seed_event_tags(db: Session, events: List[models.Event], tags: List[models.Tag]):
    """イベントとタグの関連をシード"""
    print("\n🔗 イベント-タグ関連をシード中...")

    # イベントとタグのマッピング
    event_tag_mappings = [
        # 桶狭間の戦い
        ("battle_of_okehazama", ["sengoku_period", "military_leader"]),
        # 本能寺の変
        ("honnoji_incident", ["sengoku_period"]),
        # 関ヶ原の戦い
        ("battle_of_sekigahara", ["sengoku_period", "military_leader"]),
        # フランス革命開始
        ("french_revolution_start", ["french_revolution", "politician"]),
        # ナポレオン戴冠式
        ("napoleon_crowned_emperor", ["french_revolution", "emperor"]),
        # ワーテルローの戦い
        ("battle_of_waterloo", ["french_revolution", "military_leader"]),
        # 南北戦争開始
        ("american_civil_war_start", ["american_civil_war", "military_leader"]),
        # リンカーン暗殺
        ("lincoln_assassination", ["american_civil_war", "president"]),
    ]

    # SSIDからIDへのマッピングを作成
    event_map = {e.ssid: e.id for e in events}  # type: ignore
    tag_map = {t.ssid: t.id for t in tags}  # type: ignore

    created_relations = 0
    for event_ssid, tag_ssids in event_tag_mappings:
        event_id = event_map.get(event_ssid)  # type: ignore
        if not event_id:  # type: ignore
            print(f"⚠️ イベントが見つかりません: {event_ssid}")
            continue

        for tag_ssid in tag_ssids:
            tag_id = tag_map.get(tag_ssid)  # type: ignore
            if not tag_id:  # type: ignore
                print(f"⚠️ タグが見つかりません: {tag_ssid}")
                continue

            try:
                # 中間テーブルにレコードを追加
                event_tag = models.EventTag(event_id=event_id, tag_id=tag_id)
                db.add(event_tag)
                created_relations += 1
                print(f"✓ 関連を作成: {event_ssid} - {tag_ssid}")
            except Exception as e:
                print(f"✗ 関連作成失敗: {event_ssid} - {tag_ssid} - {e}")

    db.commit()
    print(f"✅ イベント-タグ関連: {created_relations}件作成")


def seed_event_persons(db: Session, events: List[models.Event], persons: List[models.Person]):
    """イベントと人物の関連をシード"""
    print("\n🔗 イベント-人物関連をシード中...")

    # イベントと人物のマッピング（役割付き）
    event_person_mappings = [
        # 桶狭間の戦い
        ("battle_of_okehazama", [("oda_nobunaga", EventPersonRole.LEAD)]),
        # 本能寺の変
        ("honnoji_incident", [("oda_nobunaga", EventPersonRole.VICTIM)]),
        # 関ヶ原の戦い
        ("battle_of_sekigahara", [("tokugawa_ieyasu", EventPersonRole.LEAD)]),
        # ナポレオン戴冠式
        ("napoleon_crowned_emperor", [("napoleon_bonaparte", EventPersonRole.LEAD)]),
        # ワーテルローの戦い
        ("battle_of_waterloo", [("napoleon_bonaparte", EventPersonRole.LEAD)]),
        # リンカーン暗殺
        ("lincoln_assassination", [("abraham_lincoln", EventPersonRole.VICTIM)]),
    ]

    # SSIDからIDへのマッピングを作成
    event_map = {e.ssid: e.id for e in events}  # type: ignore
    person_map = {p.ssid: p.id for p in persons}  # type: ignore

    created_relations = 0
    for event_ssid, person_roles in event_person_mappings:
        event_id = event_map.get(event_ssid)  # type: ignore
        if not event_id:  # type: ignore
            print(f"⚠️ イベントが見つかりません: {event_ssid}")
            continue

        for person_ssid, role in person_roles:
            person_id = person_map.get(person_ssid)  # type: ignore
            if not person_id:  # type: ignore
                print(f"⚠️ 人物が見つかりません: {person_ssid}")
                continue

            try:
                # 中間テーブルにレコードを追加
                event_person = models.EventPerson(event_id=event_id, person_id=person_id, role=role.value)
                db.add(event_person)
                created_relations += 1
                print(f"✓ 関連を作成: {event_ssid} - {person_ssid} ({role.value})")
            except Exception as e:
                print(f"✗ 関連作成失敗: {event_ssid} - {person_ssid} - {e}")

    db.commit()
    print(f"✅ イベント-人物関連: {created_relations}件作成")


def seed_users(db: Session) -> List[User]:
    """ユーザーデータをシード"""
    print("\n👤 ユーザーデータをシード中...")

    users_data: List[dict] = [
        {
            "email": "admin@example.com",
            "username": "admin",
            "password": "adminpassword123",
            "full_name": "管理者",
            "role": UserRole.ADMIN.value,
            "is_active": True,
            "bio": "システム管理者です。",
        },
        {
            "email": "moderator@example.com",
            "username": "moderator",
            "password": "moderatorpassword123",
            "full_name": "モデレーター",
            "role": UserRole.MODERATOR.value,
            "is_active": True,
            "bio": "コンテンツモデレーターです。",
        },
        {
            "email": "user1@example.com",
            "username": "user1",
            "password": "userpassword123",
            "full_name": "一般ユーザー1",
            "role": UserRole.USER.value,
            "is_active": True,
            "bio": "一般ユーザーです。",
        },
        {
            "email": "user2@example.com",
            "username": "user2",
            "password": "userpassword123",
            "full_name": "一般ユーザー2",
            "role": UserRole.USER.value,
            "is_active": True,
            "bio": "一般ユーザーです。",
        },
        {
            "email": "user3@example.com",
            "username": "user3",
            "password": "userpassword123",
            "full_name": "一般ユーザー3",
            "role": UserRole.USER.value,
            "is_active": True,
            "bio": "一般ユーザーです。",
        },
        {
            "email": "inactive@example.com",
            "username": "inactive",
            "password": "userpassword123",
            "full_name": "非アクティブユーザー",
            "role": UserRole.USER.value,
            "is_active": False,
            "bio": "非アクティブなユーザーです。",
        },
    ]

    created_users = []
    for user_data in users_data:
        try:
            # 既存ユーザーのチェック
            if user_crud.exists(db, email=str(user_data["email"])):
                print(f"⚠️ ユーザーが既に存在します: {user_data['email']}")
                continue
            if user_crud.exists(db, username=str(user_data["username"])):
                print(f"⚠️ ユーザー名が既に存在します: {user_data['username']}")
                continue

            user = user_crud.create(db, obj_in=schemas.UserCreate(**user_data))
            created_users.append(user)
            print(f"✓ ユーザーを作成: {user.username} ({user.role})")
        except Exception as e:
            print(f"✗ ユーザー作成失敗: {user_data['username']} - {e}")

    print(f"✅ ユーザー: {len(created_users)}件作成")
    return created_users


def seed_all_data():
    """全てのデータをシード"""
    print("🌱 データベースシーディングを開始します...")

    db = SessionLocal()
    try:
        # 人物データをシード
        print("\n👥 人物データをシード中...")
        persons = seed_persons(db)

        # タグデータをシード
        print("\n🏷️ タグデータをシード中...")
        tags = seed_tags(db)

        # イベントデータをシード
        print("\n📅 イベントデータをシード中...")
        events = seed_events(db)

        # 関連データをシード
        seed_person_tags(db, persons, tags)
        seed_event_tags(db, events, tags)
        seed_event_persons(db, events, persons)

        # ユーザーデータをシード
        users = seed_users(db)

        print("\n✅ シーディング完了!")
        print(f"   人物: {len(persons)}件")
        print(f"   タグ: {len(tags)}件")
        print(f"   イベント: {len(events)}件")
        print(f"   ユーザー: {len(users)}件")

    except Exception as e:
        print(f"❌ シーディング中にエラーが発生しました: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_all_data()
