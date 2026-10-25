# Deploy do backend do So Promo Boa para a VPS Locaweb
# Uso: .\scripts\deploy-backend.ps1

$VPS_HOST = "191.252.191.189"
$VPS_USER = "root"
$VPS_KEY = "$HOME\.ssh\buscarmas_vps"
$VPS_DIR = "/opt/sopromoboa"

Write-Host "Executando testes locais..." -ForegroundColor Cyan
& ".\backend\venv\Scripts\python.exe" -m pytest backend/tests/ -q
if ($LASTEXITCODE -ne 0) {
    Write-Error "Testes falharam! Deploy abortado."
    exit 1
}

Write-Host "Criando pacote backend_deploy.tar.gz..." -ForegroundColor Cyan
tar --exclude="venv" --exclude="__pycache__" --exclude=".pytest_cache" --exclude="*.log" --exclude="*.db-shm" --exclude="*.db-wal" -czf backend_deploy.tar.gz -C backend .

Write-Host "Enviando para a VPS ($VPS_HOST)..." -ForegroundColor Cyan
scp -i $VPS_KEY backend_deploy.tar.gz "$VPS_USER@$VPS_HOST`:$VPS_DIR/backend_deploy.tar.gz"

Remove-Item -Force backend_deploy.tar.gz

Write-Host "Extraindo e reiniciando servicos na VPS..." -ForegroundColor Cyan
ssh -i $VPS_KEY -o BatchMode=yes "$VPS_USER@$VPS_HOST" "cd $VPS_DIR && tar -xzf backend_deploy.tar.gz && rm backend_deploy.tar.gz && cp -n .env.vps .env 2>/dev/null || true && cp docker-compose.vps.yml docker-compose.yml && docker compose restart api worker"

Write-Host "Deploy concluido com sucesso!" -ForegroundColor Green
