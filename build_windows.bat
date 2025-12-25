@echo off
TITLE Music Downloader Builder
CLS

ECHO ===================================================
ECHO       Music Downloader - Build Script
ECHO ===================================================
ECHO.

:: Check environment
IF NOT EXIST "venv\Scripts\python.exe" (
    ECHO [ERROR] Virtual environment missing! Please run 'run_windows.bat' first to setup.
    PAUSE
    EXIT /B
)

ECHO [INFO] Installing Build Tools (PyInstaller)...
venv\Scripts\python -m pip install pyinstaller

ECHO [INFO] Cleaning previous builds...
IF EXIST "dist" RMDIR /S /Q "dist"
IF EXIST "build" RMDIR /S /Q "build"
IF EXIST "musicdl.spec" DEL "musicdl.spec"

ECHO [INFO] Building Executable...
:: Using --onefile to create a single .exe
:: Using --noconsole to hide the terminal window (optional, maybe keep it for debugging for now)
venv\Scripts\python -m PyInstaller src\main.py --name=musicdl --onefile --noconsole --clean

IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO [ERROR] Build failed!
    PAUSE
    EXIT /B
)

ECHO.
ECHO ===================================================
ECHO    Build Success! 
ECHO    Executable is in the 'dist' folder.
ECHO ===================================================
ECHO.
PAUSE
