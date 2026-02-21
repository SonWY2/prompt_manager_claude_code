@echo off
REM Simple run script

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found
    echo Please run setup_and_run_simple.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call "venv\Scripts\activate.bat"

REM Run application
echo Starting Prompt Manager...
python run.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Application exited with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)
