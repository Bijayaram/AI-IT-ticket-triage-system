@echo off
echo Starting Backend API...
cd /d D:\Capstone
set PYTHONPATH=D:\Capstone
uvicorn backend.app:app --host 0.0.0.0 --port 8000
pause
