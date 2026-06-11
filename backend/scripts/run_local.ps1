# Sobe o backend localmente (dev) na porta 48080.
# Uso: powershell -ExecutionPolicy Bypass -File scripts\run_local.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..
$env:APP_ENV = "dev"
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 48080 --reload
