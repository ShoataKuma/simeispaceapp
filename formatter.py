"""スペース挿入ロジック"""


def format_name(surname: str, given: str) -> str | None:
    """
    苗字と名前を受け取りスペース整形した文字列を返す。
    7文字以上の場合は None を返す（呼び出し側でアラート）。
    """
    total = len(surname) + len(given)

    if total >= 7:
        return None

    if total == 6:
        return surname + given

    if total == 5:
        sp = " "
        return _insert(surname, sp) + sp + _insert(given, sp)

    if total == 4:
        sp = "  "
        return _insert(surname, sp) + sp + _insert(given, sp)

    # 2・3文字: 各文字間 2sp + 境界に追加スペース
    base_sp = "  "
    extra_sp = "      " if total == 2 else "    "  # 6sp or 4sp

    surname_part = _insert(surname, base_sp)
    given_part = _insert(given, base_sp)
    boundary = base_sp + extra_sp  # 合計 8sp(2文字) or 6sp(3文字)
    return surname_part + boundary + given_part


def _insert(text: str, sep: str) -> str:
    """文字列の各文字の間に sep を挿入する"""
    return sep.join(list(text))
