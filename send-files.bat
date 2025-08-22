@echo off
REM Manual File Sender for N8N Webhook

echo ================================================
echo Manual File Sender
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python.
    pause
    exit /b 1
)

echo Select an option:
echo.
echo 1. Interactive menu (recommended)
echo 2. Send all files in audio folder
echo 3. Send specific file
echo.

set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Starting interactive file sender...
    python send_file_manually.py
) else if "%choice%"=="2" (
    echo.
    echo Sending all files in audio folder...
    python send_file_manually.py "audio/*.wav"
) else if "%choice%"=="3" (
    echo.
    set /p filepath="Enter file path: "
    python send_file_manually.py "%filepath%"
) else (
    echo Invalid choice!
    pause
    exit /b 1
)

echo.
echo File sender finished.
pause
