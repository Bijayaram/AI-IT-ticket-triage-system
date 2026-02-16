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

echo [1/2] Starting Backend API...
start "Backend API" cmd /k "cd /d D:\Capstone && set PYTHONPATH=D:\Capstone && uvicorn backend.app:app --host 0.0.0.0 --port 8000"
timeout /t 5 /nobreak >nul

echo [2/2] Starting Next.js Frontend (includes Manager Dashboard)...
start "Next.js Frontend" cmd /k "cd /d D:\Capstone\frontend && npm run dev"
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo Access Points:
echo   Backend API:         http://localhost:8000
echo   API Documentation:   http://localhost:8000/docs
echo.
echo   Customer Portal:     http://localhost:3000
echo   Track Tickets:       http://localhost:3000/track
echo   Manager Dashboard:   http://localhost:3000/manager  [NEW React/Next.js]
echo.
echo NOTE: Next.js frontend may take 30-60 seconds to fully start.
echo       Wait for "Ready on http://localhost:3000" message.
echo.
echo TIP: The Manager Dashboard is now built into the Next.js app!
echo      Access it from any page using the "Manager Dashboard" link.
echo.
echo Optional: To start the legacy Streamlit Manager Dashboard:
echo   streamlit run manager_dashboard/streamlit_dashboard.py --server.port 8502
echo.
echo Press any key to close this window...
pause >nul
