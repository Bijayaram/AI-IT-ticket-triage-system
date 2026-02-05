@echo off
echo Starting Customer Portal...
cd /d D:\Capstone
streamlit run customer_portal/streamlit_app.py --server.port 8501
pause
