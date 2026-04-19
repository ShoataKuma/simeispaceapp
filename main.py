"""氏名スペース整形ツール - Streamlit版"""
import streamlit as st

from formatter import format_name
from surname_detector import detect

st.set_page_config(page_title="氏名スペース整形ツール", layout="centered")
st.title("氏名スペース整形ツール")

if "results" not in st.session_state:
    st.session_state.results = []
if "needs_manual" not in st.session_state:
    st.session_state.needs_manual = []
if "manual_inputs" not in st.session_state:
    st.session_state.manual_inputs = {}
if "lines" not in st.session_state:
    st.session_state.lines = []


def process_names(lines: list[str], manual_overrides: dict) -> tuple[list, list]:
    results = []
    needs_manual = []

    for raw in lines:
        override = manual_overrides.get(raw, "").strip()
        if override:
            parts = override.split(None, 1)
            if len(parts) == 2:
                pair = (parts[0], parts[1])
            else:
                needs_manual.append(raw)
                results.append((raw, None, "manual_needed"))
                continue
        else:
            pair = detect(raw)
            if pair is None:
                needs_manual.append(raw)
                results.append((raw, None, "manual_needed"))
                continue

        surname, given = pair
        formatted = format_name(surname, given)
        if formatted is None:
            results.append((raw, None, "too_long"))
        else:
            results.append((raw, formatted, "ok"))

    return results, needs_manual


# --- 入力エリア ---
input_text = st.text_area(
    "【入力】Excelからペースト（1行1名）",
    height=180,
    placeholder="田中一郎\n佐藤 花子\n長谷川義雄",
)

if st.button("整　形", type="primary"):
    lines = [l.strip() for l in input_text.splitlines() if l.strip()]
    st.session_state.lines = lines
    st.session_state.manual_inputs = {}
    results, needs_manual = process_names(lines, {})
    st.session_state.results = results
    st.session_state.needs_manual = needs_manual

# --- 手動入力セクション ---
if st.session_state.needs_manual:
    st.warning(
        f"以下 {len(st.session_state.needs_manual)} 件は苗字の区切りが判定できませんでした。"
        "スペースで苗字と名前を区切って入力してください。"
    )
    for name in st.session_state.needs_manual:
        st.session_state.manual_inputs[name] = st.text_input(
            f"「{name}」→",
            value=st.session_state.manual_inputs.get(name, ""),
            placeholder=f"例: {name[:2]} {name[2:]}",
            key=f"manual_{name}",
        )

    if st.button("手動入力で再整形"):
        results, needs_manual = process_names(
            st.session_state.lines, st.session_state.manual_inputs
        )
        st.session_state.results = results
        st.session_state.needs_manual = needs_manual
        st.rerun()

# --- 結果表示 ---
if st.session_state.results:
    output_lines = []
    for raw, formatted, status in st.session_state.results:
        if status == "ok":
            output_lines.append(formatted)
        elif status == "too_long":
            st.error(f"「{raw}」は7文字以上のため処理できません。")
            output_lines.append(f"[スキップ: {raw}]")
        else:
            output_lines.append(f"[未処理: {raw}]")

    ok_count = sum(1 for _, _, s in st.session_state.results if s == "ok")
    skip_count = len(st.session_state.results) - ok_count
    st.info(f"処理完了: {ok_count} 件　／　スキップ: {skip_count} 件")

    st.text_area("【出力】（コピーして使用）", value="\n".join(output_lines), height=180)
