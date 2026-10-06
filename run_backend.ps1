# SciData Platform Backend PowerShell Runner
Set-Location -Path $PSScriptRoot

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting SciData Platform Backend Server..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if (Test-Path ".venv311\Scripts\python.exe") {
    & ".venv311\Scripts\python.exe" server.py
} else {
    python server.py
}
