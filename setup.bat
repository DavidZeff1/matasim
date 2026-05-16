@echo off
setlocal
cd /d "%~dp0"

echo ==============================================
echo  Check Splitter - First-time setup (Windows)
echo ==============================================
echo.

REM --- 1. Python check ---
where python >nul 2>&1
if errorlevel 1 (
    echo [!] Python is not installed.
    echo.
    echo Please install Python 3 from:
    echo    https://www.python.org/downloads/
    echo.
    echo IMPORTANT: on the first install screen, tick
    echo            "Add python.exe to PATH"
    echo.
    pause
    exit /b 1
)
echo [OK] Python found:
python --version
echo.

REM --- 2. Tesseract check ---
where tesseract >nul 2>&1
if errorlevel 1 (
    if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
        echo [OK] Tesseract found at C:\Program Files\Tesseract-OCR
    ) else (
        echo [!] Tesseract OCR is not installed.
        echo.
        echo Please install it from:
        echo    https://github.com/UB-Mannheim/tesseract/wiki
        echo.
        echo During install, on the "Choose components" screen, expand
        echo "Additional language data" and tick **Hebrew**.
        echo.
        echo After installing, run this setup.bat again.
        echo.
        pause
        exit /b 1
    )
) else (
    echo [OK] Tesseract found on PATH.
)
echo.

REM --- 3. Hebrew language pack check ---
set "TESS_DIR="
if exist "C:\Program Files\Tesseract-OCR\tessdata\heb.traineddata" set "TESS_DIR=C:\Program Files\Tesseract-OCR\tessdata"
if exist "C:\Program Files (x86)\Tesseract-OCR\tessdata\heb.traineddata" set "TESS_DIR=C:\Program Files (x86)\Tesseract-OCR\tessdata"
if "%TESS_DIR%"=="" (
    echo [!] Tesseract is installed but the Hebrew language pack ^(heb.traineddata^) is missing.
    echo.
    echo Re-run the Tesseract installer and on the "Choose components" screen,
    echo expand "Additional language data" and tick **Hebrew**.
    echo.
    echo Or download heb.traineddata from:
    echo    https://github.com/tesseract-ocr/tessdata/raw/main/heb.traineddata
    echo and drop it into C:\Program Files\Tesseract-OCR\tessdata\
    echo.
    pause
    exit /b 1
)
echo [OK] Hebrew language pack found.
echo.

REM --- 4. Install Python packages ---
echo Installing Python packages ^(pymupdf, pytesseract, pillow^)...
python -m pip install --user --upgrade -r requirements.txt
if errorlevel 1 (
    echo.
    echo [!] pip install failed. Check the messages above.
    pause
    exit /b 1
)
echo.
echo ==============================================
echo  Setup complete. Double-click run.bat to start.
echo ==============================================
pause
