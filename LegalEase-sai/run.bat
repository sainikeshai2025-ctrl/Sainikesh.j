@echo off
TITLE LegalEase - AI-Powered Legal Document Generator
echo ========================================================
echo        LegalEase: AI Legal Document Generator
echo ========================================================

REM Kill any previous lingering processes on ports 8000 and 8501
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8501') do taskkill /f /pid %%a >nul 2>&1

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in .\venv
    echo Creating virtual environment...
    python -m venv venv
    call .\venv\Scripts\pip install -r requirements.txt
)

echo Starting FastAPI Backend Server on port 8000...
start "LegalEase-Backend" /MIN .\venv\Scripts\python.exe -m uvicorn legalEaseAPI.main:app --host 127.0.0.1 --port 8000 --reload

echo Waiting for Backend Server to initialize...
timeout /t 3 /nobreak > nul

echo Starting Streamlit Frontend on port 8501...
.\venv\Scripts\python.exe -m streamlit run frontend/app.py --server.port 8501

REM When frontend closes, stop backend
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a >nul 2>&1
