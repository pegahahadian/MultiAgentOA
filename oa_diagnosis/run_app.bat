@echo off
REM OA Diagnosis System - Chainlit App Launcher
REM This script starts the Chainlit UI for the OA Diagnosis System

echo ========================================
echo  OA Diagnosis System - Chainlit Startup
echo ========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Navigate to the AutoGen root directory (parent of oa_diagnosis)
cd /d "%SCRIPT_DIR%.."

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Start Chainlit
echo Starting Chainlit on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python -m chainlit run oa_diagnosis/app.py --port 8000

pause
