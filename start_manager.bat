@echo off
echo Starting Manager Dashboard...
cd /d D:\Capstone
streamlit run manager_dashboard/streamlit_dashboard.py --server.port 8502
pause
