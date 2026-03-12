@echo off
echo ============================================================
echo  MD-ADSS Backend — Amazon Nova AI Hackathon
echo ============================================================

cd /d "%~dp0backend"

:: Create virtualenv if it doesn't exist
if not exist venv (
    echo [1/3] Creating Python virtual environment...
    python -m venv venv
)

:: Activate and install dependencies
echo [2/3] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

:: Start the server
echo [3/3] Starting FastAPI server on http://localhost:8000
echo       API docs: http://localhost:8000/docs
echo.
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
