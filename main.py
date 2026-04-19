"""氏名スペース整形ツール - Streamlit版"""
import streamlit as st

from formatter import format_name
from surname_detector import detect

st.set_page_config(page_title="氏名スペース整形ツール", layout="centered")
st.title("氏名スペース整形ツール")

if "results" not in st.session_state:
    st.session_state.results = []       # list of (raw, formatted, status)
if "pending_splits" not in st.session_state:
    st.session_state.pending_splits = {}  # raw_name -> split_position (int)
if "lines" not in st.session_state:
    st.session_state.lines = []


def process_one(raw: str, manual_split: int | None = None) -> tuple[str | None, str]:
    """
    1名分を処理して (formatted | None, status) を返す。
    status: "ok" | "too_long" | "need_split"
    """
    clean = raw.replace(" ", "").replace("\u3000", "")
    total = len(clean)

    if total >= 7:
        return None, "too_long"

    # 4文字以上・2文字は境界位置が結果に影響しないので苗字判定不要
    if total != 3:
        result = format_name(clean[0], clean[1:])
        return result, "ok"

    # --- 3文字のみ境界を特定する ---
    # 1. 入力にスペースがあればそれを使用
    parts = raw.split()
    if len(parts) == 2 and len(parts[0]) + len(parts[1]) == 3:
        return format_name(parts[0], parts[1]), "ok"

    # 2. 苗字辞書で前方一致
    pair = detect(clean)
    if pair and len(pair[0]) + len(pair[1]) == 3:
        return format_name(pair[0], pair[1]), "ok"

    # 3. 手動指定済みならその位置で分割（文字は原文から取得）
    if manual_split is not None:
        return format_name(clean[:manual_split], clean[manual_split:]), "ok"

    return None, "need_split"


def run_process(lines: list[str], manual_splits: dict) -> tuple[list, dict]:
    results = []
    still_pending = {}

    for raw in lines:
        clean = raw.replace(" ", "").replace("\u3000", "")
        split = manual_splits.get(clean)
        formatted, status = process_one(raw, split)
        results.append((raw, formatted, status))
        if status == "need_split":
            still_pending[clean] = split  # None のまま保持

    return results, still_pending


# ============================================================
# 入力エリア
# ============================================================
input_text = st.text_area(
    "【入力】Excelからペースト（1行1名）",
    height=180,
    placeholder="田中一郎\n佐藤 花子\n長谷川義雄",
)

if st.button("整　形", type="primary"):
    lines = [l.strip() for l in input_text.splitlines() if l.strip()]
    st.session_state.lines = lines
    st.session_state.pending_splits = {}
    results, pending = run_process(lines, {})
    st.session_state.results = results
    st.session_state.pending_splits = pending

# ============================================================
# 手動区切り指定セクション（3文字・苗字不明のみ）
# ============================================================
need_split_items = [
    (raw, clean)
    for raw, formatted, status in st.session_state.results
    if status == "need_split"
    for clean in [raw.replace(" ", "").replace("\u3000", "")]
]

if need_split_items:
    st.warning(f"以下 {len(need_split_items)} 件は苗字の区切りが判定できませんでした。区切り位置を選んでください。")

    updated = False
    for raw, clean in need_split_items:
        # 3文字なので選択肢は「1文字目で切る」か「2文字目で切る」の2択
        options = {
            f"{clean[0]} ／ {clean[1:]}": 1,
            f"{clean[:2]} ／ {clean[2]}": 2,
        }
        current_split = st.session_state.pending_splits.get(clean)
        current_label = next((k for k, v in options.items() if v == current_split), None)

        chosen = st.radio(
            f"「{clean}」の苗字と名前の区切り",
            list(options.keys()),
            index=list(options.keys()).index(current_label) if current_label else 0,
            horizontal=True,
            key=f"split_{clean}",
        )
        new_split = options[chosen]
        if st.session_state.pending_splits.get(clean) != new_split:
            st.session_state.pending_splits[clean] = new_split
            updated = True

    if st.button("区切りを確定して再整形"):
        results, pending = run_process(
            st.session_state.lines, st.session_state.pending_splits
        )
        st.session_state.results = results
        st.session_state.pending_splits = pending
        st.rerun()

# ============================================================
# 結果表示
# ============================================================
if st.session_state.results:
    output_lines = []
    for raw, formatted, status in st.session_state.results:
        if status == "ok":
            output_lines.append(formatted)
        elif status == "too_long":
            clean = raw.replace(" ", "")
            st.error(f"「{clean}」は {len(clean)} 文字（7文字以上）のため処理できません。")
            output_lines.append(f"[スキップ: {clean}]")
        else:
            output_lines.append(f"[区切り未指定: {raw}]")

    ok_count = sum(1 for _, _, s in st.session_state.results if s == "ok")
    skip_count = len(st.session_state.results) - ok_count
    st.info(f"処理完了: {ok_count} 件　／　スキップ・未処理: {skip_count} 件")

    st.text_area("【出力】（コピーして使用）", value="\n".join(output_lines), height=180)
