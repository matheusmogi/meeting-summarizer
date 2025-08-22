@echo off
REM Meeting Recorder - System Tray Launcher

echo ================================================
echo Meeting Recorder - System Tray
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python.
    pause
    exit /b 1
)

REM Install required packages if missing
echo Checking required packages...

python -c "import pystray" 2>nul
if errorlevel 1 (
    echo Installing pystray...
    pip install pystray
)

python -c "import PIL" 2>nul
if errorlevel 1 (
    echo Installing Pillow...
    pip install pillow
)

python -c "import keyboard" 2>nul
if errorlevel 1 (
    echo Installing keyboard...
    pip install keyboard
)

python -c "import requests" 2>nul
if errorlevel 1 (
    echo Installing requests...
    pip install requests
)

python -c "import psutil" 2>nul
if errorlevel 1 (
    echo Installing psutil...
    pip install psutil
)

echo.
echo Starting Meeting Recorder in system tray...
echo - Look for the microphone icon in your system tray
echo - Right-click the icon for menu options
echo - Use Ctrl+Shift+R hotkey to start/stop recording
echo - Close this window or use tray menu to exit
echo.

REM Run the tray application
python tray_recorder.py

echo.
echo Tray recorder stopped.
pause
