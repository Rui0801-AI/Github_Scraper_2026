@echo off
title GitHub Scraper 2026
cd /d "%~dp0"

REM Check for Python virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Check if requirements are installed
pip show requests >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Run the main script
python main.py
pause