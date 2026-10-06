@echo off
cd /d "%~dp0platform\frontend"
echo ============================================================
echo Starting SciData Platform Frontend...
echo Access in browser: http://localhost:3000
echo ============================================================
set NODE_OPTIONS=--no-deprecation
set PORT=3000
npm start
