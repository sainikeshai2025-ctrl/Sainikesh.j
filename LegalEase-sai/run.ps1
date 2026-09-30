# LegalEase Launch Script for PowerShell
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       LegalEase: AI Legal Document Generator           " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Clean up any previous lingering processes on ports 8000 and 8501
Get-NetTCPConnection -LocalPort 8000, 8501 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}

$pythonPath = ".\venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Host "[INFO] Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    .\venv\Scripts\pip install -r requirements.txt
}

Write-Host "Starting FastAPI Backend Server on port 8000..." -ForegroundColor Green
$backendProcess = Start-Process -FilePath $pythonPath -ArgumentList "-m uvicorn legalEaseAPI.main:app --host 127.0.0.1 --port 8000 --reload" -PassThru

Start-Sleep -Seconds 3

Write-Host "Starting Streamlit Frontend on port 8501..." -ForegroundColor Green
try {
    & $pythonPath -m streamlit run frontend/app.py --server.port 8501
} finally {
    if ($backendProcess -and -not $backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
}
