@echo off
TITLE Music Downloader Launcher
CLS

ECHO ===================================================
ECHO       Music Downloader - Windows Launcher
ECHO ===================================================
ECHO.

:: Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] Python is not found! 
    ECHO Please install Python 3.10+ from python.org and check "Add Python to PATH".
    PAUSE
    EXIT /B
)

:: Check if venv exists
IF NOT EXIST "venv" (
    ECHO [INFO] Virtual environment not found. Creating one...
    python -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        ECHO [ERROR] Failed to create virtual environment.
        PAUSE
        EXIT /B
    )
    ECHO [INFO] Installing dependencies...
    venv\Scripts\python -m pip install --upgrade pip
    venv\Scripts\python -m pip install -r requirements.txt
) ELSE (
    :: Check if venv is healthy (has python.exe)
    IF NOT EXIST "venv\Scripts\python.exe" (
        ECHO [WARNING] Virtual environment appears corrupted. Recreating...
        RMDIR /S /Q venv
        python -m venv venv
        ECHO [INFO] Installing dependencies...
        venv\Scripts\python -m pip install --upgrade pip
        venv\Scripts\python -m pip install -r requirements.txt
    )
)

:: Run the App
ECHO.
ECHO [INFO] Launching Music Downloader...
venv\Scripts\python src\main.py

IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO [ERROR] The application crashed or closed unexpectedly.
    PAUSE
)
