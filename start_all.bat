@echo off
echo ========================================
echo IT Ticket Triage System - Startup
echo ========================================
echo.

echo Starting all services...
echo Please wait for all services to start before accessing the web apps.
echo.

echo [1/3] Starting Backend API...
start "Backend API" cmd /k "python backend/app.py"
timeout /t 5 /nobreak >nul

echo [2/3] Starting Customer Portal...
start "Customer Portal" cmd /k "streamlit run customer_portal/streamlit_app.py --server.port 8501"
timeout /t 3 /nobreak >nul

echo [3/3] Starting Manager Dashboard...
start "Manager Dashboard" cmd /k "streamlit run manager_dashboard/streamlit_dashboard.py --server.port 8502"

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo Access points:
echo   Customer Portal:   http://localhost:8501
echo   Manager Dashboard: http://localhost:8502
echo   API Documentation: http://localhost:8000/docs
echo.
echo Press any key to close this window...
pause >nul
