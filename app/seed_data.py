"""
データベースシーディングスクリプト

歴史的人物、イベント、タグのサンプルデータをデータベースに投入します。
"""

from datetime import date
from typing import List

from sqlalchemy.orm import Session

from . import models, schemas
from .crud import EventCRUD, PersonCRUD, TagCRUD
from .database import SessionLocal


def seed_persons(db: Session) -> List[models.Person]:
    """人物データをシード"""
    person_crud = PersonCRUD()

    persons_data = [
        {
            "ssid": "oda_nobunaga",
            "full_name": "織田信長",
            "display_name": "信長",
            "birth_date": date(1534, 6, 23),
            "death_date": date(1582, 6, 21),
            "born_country": "日本",
            "born_region": "尾張国",
            "description": "戦国時代の武将。天下統一を目指した戦国大名。",
        },
        {
            "ssid": "toyotomi_hideyoshi",
            "full_name": "豊臣秀吉",
            "display_name": "秀吉",
            "birth_date": date(1537, 3, 17),
            "death_date": date(1598, 9, 18),
            "born_country": "日本",
            "born_region": "尾張国",
            "description": "織田信長の家臣から天下人となった武将。",
        },
        {
            "ssid": "tokugawa_ieyasu",
            "full_name": "徳川家康",
            "display_name": "家康",
            "birth_date": date(1543, 1, 31),
            "death_date": date(1616, 6, 1),
            "born_country": "日本",
            "born_region": "三河国",
            "description": "江戸幕府を開いた初代将軍。",
        },
        {
            "ssid": "napoleon_bonaparte",
            "full_name": "ナポレオン・ボナパルト",
            "display_name": "ナポレオン",
            "birth_date": date(1769, 8, 15),
            "death_date": date(1821, 5, 5),
            "born_country": "フランス",
            "born_region": "コルシカ島",
            "description": "フランスの軍人・政治家。フランス第一帝政の皇帝。",
        },
        {
            "ssid": "abraham_lincoln",
            "full_name": "エイブラハム・リンカーン",
            "display_name": "リンカーン",
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

        print("\n✅ シーディング完了!")
        print(f"   人物: {len(persons)}件")
        print(f"   タグ: {len(tags)}件")
        print(f"   イベント: {len(events)}件")

    except Exception as e:
        print(f"❌ シーディング中にエラーが発生しました: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_all_data()
