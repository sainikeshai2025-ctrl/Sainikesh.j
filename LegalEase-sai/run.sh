#!/usr/bin/env bash
# LegalEase Launch Script for Linux / macOS / Bash
echo "========================================================"
echo "       LegalEase: AI Legal Document Generator           "
echo "========================================================"

if [ -d "venv" ]; then
    source venv/bin/activate || source venv/Scripts/activate
fi

echo "Starting FastAPI Backend Server on port 8000..."
python -m uvicorn legalEaseAPI.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

sleep 3

echo "Starting Streamlit Frontend on port 8501..."
streamlit run frontend/app.py --server.port 8501

kill $BACKEND_PID
