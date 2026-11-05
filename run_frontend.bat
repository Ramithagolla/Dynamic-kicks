@echo off
echo ========================================================
echo Starting ThreatLens AI Frontend (React + Vite)
echo Host: 0.0.0.0  Port: 5173
echo ========================================================
cd /d "%~dp0\frontend"
npm run dev -- --host 0.0.0.0 --port 5173
pause
