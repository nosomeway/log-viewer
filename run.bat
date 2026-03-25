@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动 log-viewer（请勿关闭本窗口）...
echo 浏览器打开: http://127.0.0.1:8000/
echo.
pip install -r requirements.txt -q
uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
