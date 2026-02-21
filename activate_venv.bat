@echo off
REM [overview]
REM Virtual Environment Activation Script (Windows)
REM
REM [description]
REM Activates the Python virtual environment for Prompt Manager.
REM Use this when manually running Python scripts or executing tests.

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

echo Virtual environment activated.
echo Current Python:
python --version
echo.
echo Enter commands below. (Type 'exit' to quit)
cmd /k

endlocal
