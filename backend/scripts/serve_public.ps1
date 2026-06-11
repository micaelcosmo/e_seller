# Sobe o backend (porta 48080) e publica um link HTTPS via Cloudflare Tunnel (quick mode).
# NÃO exige conta nem custo (URL temporária trycloudflare).
# Uso: powershell -ExecutionPolicy Bypass -File scripts\serve_public.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$cloudflared = ".\.tools\cloudflared.exe"
if (-not (Test-Path $cloudflared)) {
    Write-Output "Baixando cloudflared..."
    New-Item -ItemType Directory -Force -Path .tools | Out-Null
    $url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    Invoke-WebRequest -Uri $url -OutFile $cloudflared -UseBasicParsing
}

# Inicia o servidor em segundo plano.
$env:APP_ENV = "dev"
Start-Process -FilePath ".\.venv\Scripts\python.exe" `
    -ArgumentList "-m","uvicorn","app.main:app","--host","0.0.0.0","--port","48080" `
    -WindowStyle Hidden

Start-Sleep -Seconds 3
Write-Output "Backend em http://localhost:48080  (docs: /docs)"
Write-Output "Abrindo tunel publico (aguarde a URL https://*.trycloudflare.com)..."

# Abre o túnel (mostra a URL pública no console).
& $cloudflared tunnel --url http://localhost:48080
