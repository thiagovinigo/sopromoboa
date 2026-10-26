#!/usr/bin/env bash
# Deploy do backend So Promo Boa para a VPS Locaweb
set -euo pipefail

VPS_HOST="${VPS_HOST:-191.252.191.189}"
VPS_USER="${VPS_USER:-root}"
VPS_KEY="${VPS_KEY:-$HOME/.ssh/buscarmas_vps}"
VPS_DIR="${VPS_DIR:-/opt/sopromoboa}"

echo "Rodando testes locais..."
pytest backend/tests/ -q

echo "Criando pacote backend_deploy.tar.gz..."
tar --exclude="venv" --exclude="__pycache__" --exclude=".pytest_cache" --exclude="*.log" --exclude=".env" --exclude="*.db" --exclude="*.db-shm" --exclude="*.db-wal" -czf backend_deploy.tar.gz -C backend .

echo "Enviando para a VPS ($VPS_HOST)..."
scp -i "$VPS_KEY" backend_deploy.tar.gz "$VPS_USER@$VPS_HOST:$VPS_DIR/backend_deploy.tar.gz"
rm -f backend_deploy.tar.gz

echo "Extraindo e reiniciando servicos na VPS..."
ssh -i "$VPS_KEY" -o BatchMode=yes "$VPS_USER@$VPS_HOST" "cd $VPS_DIR && tar -xzf backend_deploy.tar.gz && rm backend_deploy.tar.gz && cp -n .env.vps .env 2>/dev/null || true && cp docker-compose.vps.yml docker-compose.yml && docker compose up -d api worker"

echo "Deploy concluido com sucesso!"
