# SciData Platform Frontend PowerShell Runner
Set-Location -Path "$PSScriptRoot\platform\frontend"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting SciData Platform Frontend..." -ForegroundColor Cyan
Write-Host "Access in browser at: http://localhost:3000" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

$env:NODE_OPTIONS = "--no-deprecation"
$env:PORT = "3000"
npm start
