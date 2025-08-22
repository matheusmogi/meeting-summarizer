@echo off
REM FFmpeg Audio Recorder Launcher

echo ================================================
echo FFmpeg Audio Recorder
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python.
    pause
    exit /b 1
)

REM Check FFmpeg
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ERROR: FFmpeg not found!
    echo Please install FFmpeg: https://ffmpeg.org/download.html
    echo Make sure it's added to your PATH
    pause
    exit /b 1
)

REM Install requests if needed
python -c "import requests" 2>nul
if errorlevel 1 (
    echo Installing requests package...
    pip install requests
)

echo Starting FFmpeg audio recorder...
echo - Records microphone + system audio simultaneously
echo - Automatically uploads to N8N webhook when stopped
echo - Deletes files after successful upload
echo.
echo REQUIREMENTS:
echo - VB-Audio Virtual Cable must be installed and configured
echo - Microphone: "Microphone (USB PnP Sound Device)"
echo - System Audio: "CABLE Output (VB-Audio Virtual Cable)"
echo.
echo Press Ctrl+C to stop recording
echo.

REM Run the FFmpeg recorder
python ffmpeg_recorder.py

echo.
echo FFmpeg recording session ended.
pause
