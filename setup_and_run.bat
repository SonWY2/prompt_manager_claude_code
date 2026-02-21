@echo off
REM [overview]
REM Prompt Manager Initial Setup and Run Script (Windows)
REM
REM [description]
REM Creates virtual environment, installs required dependencies, then runs the application.
REM Use this on first run or when resetting the environment.

chcp 65001 >nul
setlocal enabledelayedexpansion

REM Set project root directory
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo ========================================
echo Prompt Manager Installation and Run
echo ========================================
echo.

REM Step 1: Check and create virtual environment
echo [1/3] Checking virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment does not exist. Starting creation...
    python --version >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Python is not installed.
        echo Please install Python 3.12+ and try again.
        echo Download: https://www.python.org/downloads/
        pause
        exit /b 1
    )

    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
call "venv\Scripts\activate.bat"

REM Step 2: Install dependencies
echo.
echo [2/3] Checking dependencies...
echo Upgrading pip...
python -m pip install --upgrade pip

if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed successfully
) else (
    echo [WARNING] requirements.txt not found. Skipping dependency installation.
)

REM Step 3: Run application
echo.
echo [3/3] Starting Prompt Manager application...
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
