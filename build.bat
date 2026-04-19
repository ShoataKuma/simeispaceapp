@echo off
chcp 65001 > nul
echo ===== EXE ビルド開始 =====

pip install pyinstaller -q

pyinstaller ^
  --onefile ^
  --windowed ^
  --name "氏名整形ツール" ^
  --add-data "surnames.json;." ^
  main.py

echo.
echo ===== 完了 =====
echo dist\氏名整形ツール.exe が生成されました
pause
