@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3.11-3.13 is required. Install Python with the Windows launcher first.
  pause
  exit /b 1
)
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -c "import sys; assert (3,11) <= sys.version_info[:2] <= (3,13), 'Use Python 3.11, 3.12 or 3.13.'"
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -c "import streamlit, mysql.connector, pandas, dotenv" >nul 2>nul
if errorlevel 1 .venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
if not exist .env .venv\Scripts\python.exe scripts\setup.py
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe scripts\doctor.py
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m streamlit run app.py
pause
