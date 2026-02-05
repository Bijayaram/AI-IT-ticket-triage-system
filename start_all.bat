@echo off
echo ========================================
echo IT Ticket Triage System - Startup
echo ========================================
echo.

cd /d D:\Capstone
set PYTHONPATH=D:\Capstone

echo Starting all services...
echo Please wait for all services to start before accessing the web apps.
echo.

echo [1/3] Starting Backend API...
start "Backend API" cmd /k "cd /d D:\Capstone && set PYTHONPATH=D:\Capstone && uvicorn backend.app:app --host 0.0.0.0 --port 8000"
timeout /t 5 /nobreak >nul

echo [2/3] Starting Next.js Frontend...
start "Next.js Frontend" cmd /k "cd /d D:\Capstone\frontend && npm run dev"
timeout /t 5 /nobreak >nul

echo [3/3] Starting Manager Dashboard (Streamlit)...
start "Manager Dashboard" cmd /k "cd /d D:\Capstone && streamlit run manager_dashboard/streamlit_dashboard.py --server.port 8502"

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo Access points:
echo   Backend API:        http://localhost:8000
echo   Customer Frontend:  http://localhost:3000  [NEW Next.js]
echo   Manager Dashboard:  http://localhost:8502  [Streamlit]
echo   API Documentation:  http://localhost:8000/docs
echo.
echo NOTE: Next.js frontend may take 30-60 seconds to start.
echo       Wait for "Ready on http://localhost:3000" message.
echo.
echo Press any key to close this window...
pause >nul
