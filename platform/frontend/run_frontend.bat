@echo off
cd /d "%~dp0"
echo ============================================================
echo Starting SciData Platform Frontend...
echo Access in browser at: http://localhost:3000
echo ============================================================
set NODE_OPTIONS=--no-deprecation
set PORT=3000
npm start
