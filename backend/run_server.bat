@echo off
set "VENV_PYTHON=c:\Users\SIDDHESHWAR DUBEY\Documents\CODES\Projects\GigShield\gigShield\gigshield\Scripts\python.exe"
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul
del server.log 2>nul
echo Starting server...
"%VENV_PYTHON%" app.py > server.log 2>&1
