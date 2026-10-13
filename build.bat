@echo off
rem 打包成單一 exe，輸出在 dist\piscout.exe
rem 需要先：pip install -r requirements.txt pyinstaller

pyinstaller --noconfirm --clean --onefile --windowed --uac-admin ^
  --name piscout ^
  --add-data "piscout\static;piscout\static" ^
  --add-data "piscout\agent;piscout\agent" ^
  --collect-submodules uvicorn ^
  --collect-submodules websockets ^
  --collect-submodules pyfatfs ^
  --hidden-import passlib.handlers.sha2_crypt ^
  run_gui.py
