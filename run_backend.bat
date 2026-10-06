@echo off
cd /d "%~dp0"
echo Starting SciData Platform Backend Server...
if exist ".venv311\Scripts\python.exe" (
    ".venv311\Scripts\python.exe" server.py
) else (
    python server.py
)
pause
