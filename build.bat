@echo off
rem 打包成資料夾版（啟動比單一 exe 快），輸出在 dist\piscout\piscout.exe
rem 需要先：pip install -r requirements.txt pyinstaller

pyinstaller --noconfirm --clean --onedir --windowed ^
  --name piscout ^
  --icon packaging\installer\piscout.ico ^
  --add-data "piscout\static;piscout\static" ^
  --add-data "piscout\agent;piscout\agent" ^
  --collect-submodules uvicorn ^
  --collect-submodules websockets ^
  --collect-submodules pyfatfs ^
  --hidden-import passlib.handlers.sha2_crypt ^
  run_gui.py
