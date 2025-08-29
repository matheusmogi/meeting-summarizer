@echo off
REM Audio Sender Batch Script
REM This script makes it easy to run the audio sender on Windows

echo ======================================
echo       Audio Sender for n8n
echo ======================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if the audio_sender.py exists
if not exist "audio_sender.py" (
    echo ERROR: audio_sender.py not found in current directory
    echo Please run this script from the meeting-recorder folder
    pause
    exit /b 1
)

REM Check if config.json exists
if not exist "config.json" (
    echo ERROR: config.json not found
    echo Please copy config.example.json to config.json and configure it
    pause
    exit /b 1
)

echo Starting Audio Sender...
echo.

REM Run the audio sender with default settings
python audio_sender.py

echo.
echo ======================================
echo          Process Complete
echo ======================================
pause
