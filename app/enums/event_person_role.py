"""
イベントにおける人物の役割を定義するEnum

EventPerson中間テーブルで使用する役割を管理します。
"""

from enum import Enum


class EventPersonRole(str, Enum):
    """イベントにおける人物の役割"""

    # 主要な役割
    LEAD = "主役"  # 出来事の中心人物
    SUPPORTING = "関係者"  # 出来事に関わった人物
    WITNESS = "目撃者"  # 出来事を目撃した人物

    # 立場による分類
    VICTIM = "被害者"  # 出来事で被害を受けた人物
    PERPETRATOR = "加害者"  # 出来事を引き起こした人物
    BENEFICIARY = "受益者"  # 出来事で利益を得た人物

    # 戦闘・軍事関連
    COMMANDER = "指揮官"  # 軍事指揮官
    SOLDIER = "兵士"  # 一般兵士
    ADVISOR = "参謀"  # 軍事参謀

    # 政治・社会関連
    LEADER = "指導者"  # 政治・社会的指導者
    OFFICIAL = "役人"  # 政府役人
    CITIZEN = "市民"  # 一般市民

    # その他
    OTHER = "その他"  # その他の役割

    @classmethod
    def get_display_name(cls, role: str) -> str:
        """役割の表示名を取得"""
        try:
            return cls(role).value
        except ValueError:
            return role

    @classmethod
    def get_choices(cls) -> list[tuple[str, str]]:
        """選択肢のリストを取得（フォーム用）"""
        return [(role.value, role.value) for role in cls]

    @classmethod
    def is_valid(cls, role: str) -> bool:
        """役割が有効かチェック"""
        return role in [r.value for r in cls]
