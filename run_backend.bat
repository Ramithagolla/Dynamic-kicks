@echo off
echo ========================================================
echo Starting ThreatLens AI Backend (FastAPI + Uvicorn)
echo Host: 0.0.0.0  Port: 8000
echo ========================================================
cd /d "%~dp0\backend"
set PYTHONPATH=%~dp0\backend;%PYTHONPATH%
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
