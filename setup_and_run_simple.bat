@echo off
REM Simple setup and run script without UTF-8 issues

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ========================================
echo Prompt Manager Setup and Run
echo ========================================
echo.

REM Step 1: Check Python
echo [1/3] Checking Python installation...
python --version
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.12+ from: https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
echo Python is installed.
echo.

REM Step 2: Check/Create virtual environment
echo [2/3] Checking virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo.
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
echo.

REM Step 3: Activate virtual environment
echo Activating virtual environment...
call "venv\Scripts\activate.bat"
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated.
echo.

REM Step 4: Install dependencies
echo [3/3] Installing dependencies...
echo Upgrading pip...
python -m pip install --upgrade pip

if exist "requirements.txt" (
    echo Installing packages from requirements.txt...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo.
        echo ERROR: Failed to install dependencies
        echo You can try running this manually later
    )
) else (
    echo WARNING: requirements.txt not found
)
echo.

REM Step 5: Run application
echo ========================================
echo Starting Prompt Manager...
echo ========================================
echo.

python run.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Application exited with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Application closed normally.
pause
