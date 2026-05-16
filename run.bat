@echo off
setlocal
cd /d "%~dp0"

echo Starting Check Splitter on http://127.0.0.1:8000 ...
echo.
echo Leave this window open while using the tool.
echo Close this window to stop the server.
echo.

REM Open the browser after a short delay so the server has time to bind
start "" /b cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000"

python server.py
if errorlevel 1 (
    echo.
    echo [!] Server stopped with an error. If this is your first run,
    echo     double-click setup.bat first.
    pause
)
