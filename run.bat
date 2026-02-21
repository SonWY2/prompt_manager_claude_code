@echo off
REM [overview]
REM Prompt Manager Windows Run Script
REM
REM [description]
REM Activates virtual environment and starts Prompt Manager application.
REM Virtual environment and dependencies must already be installed.

chcp 65001 >nul
setlocal enabledelayedexpansion

REM Set project root directory
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment does not exist.
    echo Please run setup_and_run.bat first to create the virtual environment.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call "venv\Scripts\activate.bat"

REM Run application
echo [START] Starting Prompt Manager application...
echo.

python run.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Error occurred while running the application.
    echo Error code: %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

endlocal
