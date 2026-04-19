"""氏名スペース整形ツール"""
import tkinter as tk
from tkinter import messagebox, simpledialog

from formatter import format_name
from surname_detector import detect


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("氏名スペース整形ツール")
        self.resizable(True, True)
        self.minsize(520, 480)
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 4}

        tk.Label(self, text="【入力】Excelからペースト（1行1名）", anchor="w").pack(fill="x", **pad)

        self.input_text = tk.Text(self, height=10, font=("Meiryo", 11), undo=True)
        self.input_text.pack(fill="both", expand=True, padx=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="　整　形　", font=("Meiryo", 11, "bold"),
                  command=self._process).pack(side="left", padx=8)
        tk.Button(btn_frame, text="クリア", font=("Meiryo", 10),
                  command=self._clear).pack(side="left", padx=4)

        tk.Label(self, text="【出力】", anchor="w").pack(fill="x", **pad)

        self.output_text = tk.Text(self, height=10, font=("Meiryo", 11), state="disabled")
        self.output_text.pack(fill="both", expand=True, padx=10)

        bottom = tk.Frame(self)
        bottom.pack(pady=6)
        tk.Button(bottom, text="全コピー", font=("Meiryo", 10),
                  command=self._copy_all).pack(side="left", padx=8)

        self.status_var = tk.StringVar(value="準備完了")
        tk.Label(self, textvariable=self.status_var, anchor="w",
                 fg="gray").pack(fill="x", padx=10, pady=(0, 6))

    def _process(self):
        raw = self.input_text.get("1.0", "end").strip()
        if not raw:
            return

        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        results = []
        ok = warn = 0

        for line in lines:
            result = self._format_one(line)
            results.append(result if result is not None else f"[エラー: {line}]")
            if result is None:
                warn += 1
            else:
                ok += 1

        self._set_output("\n".join(results))
        self.status_var.set(f"処理完了: {ok} 件  /  警告: {warn} 件")

    def _format_one(self, raw_name: str) -> str | None:
        pair = detect(raw_name)

        if pair is None:
            # 手動入力ダイアログ
            pair = self._ask_manual(raw_name)
            if pair is None:
                return None

        surname, given = pair
        result = format_name(surname, given)

        if result is None:
            total = len(surname) + len(given)
            messagebox.showwarning(
                "文字数超過",
                f"「{raw_name}」は合計 {total} 文字（7文字以上）のため処理できません。"
            )
            return None

        return result

    def _ask_manual(self, name: str) -> tuple[str, str] | None:
        answer = simpledialog.askstring(
            "苗字・名前の区切りが不明",
            f"「{name}」の苗字と名前の間にスペースを入れてください。\n例: 田中 一郎",
            parent=self
        )
        if not answer:
            return None
        parts = answer.split()
        if len(parts) < 2:
            messagebox.showerror("入力エラー", "苗字と名前をスペースで区切って入力してください。")
            return None
        return parts[0], "".join(parts[1:])

    def _set_output(self, text: str):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.config(state="disabled")

    def _copy_all(self):
        content = self.output_text.get("1.0", "end").strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.status_var.set("クリップボードにコピーしました")

    def _clear(self):
        self.input_text.delete("1.0", "end")
        self._set_output("")
        self.status_var.set("準備完了")


if __name__ == "__main__":
    app = App()
    app.mainloop()
