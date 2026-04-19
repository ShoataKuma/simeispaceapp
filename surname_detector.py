"""苗字検出ロジック"""
import json
import os
import sys


def _load_surnames() -> list[str]:
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "surnames.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


_SURNAMES: list[str] | None = None


def get_surnames() -> list[str]:
    global _SURNAMES
    if _SURNAMES is None:
        _SURNAMES = _load_surnames()
    return _SURNAMES


def detect(full_name: str) -> tuple[str, str] | None:
    """
    スペースで分割できればそれを使用。
    スペースがない場合は苗字一覧で前方一致検索（長い苗字優先）。
    見つからなければ None を返す。
    """
    # スペース区切りがある場合
    parts = full_name.split()
    if len(parts) == 2:
        return parts[0], parts[1]
    if len(parts) > 2:
        # スペースが複数：先頭を苗字、残りを名前として結合
        return parts[0], "".join(parts[1:])

    # スペースなし → 苗字一覧で前方一致（長い苗字を優先: JSONは長さ降順）
    for surname in get_surnames():
        if full_name.startswith(surname):
            given = full_name[len(surname):]
            if given:  # 名前部分が空でないこと
                return surname, given

    return None
