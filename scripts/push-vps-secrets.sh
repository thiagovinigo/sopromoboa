#!/usr/bin/env bash
# Copia segredos selecionados de backend/.env (local) para /opt/sopromoboa/.env na VPS.
# Os valores nunca são impressos. Uso: bash scripts/push-vps-secrets.sh
set -euo pipefail

VPS_HOST="${VPS_HOST:-191.252.191.189}"
VPS_USER="${VPS_USER:-root}"
VPS_KEY="${VPS_KEY:-$HOME/.ssh/buscarmas_vps}"
VPS_DIR="${VPS_DIR:-/opt/sopromoboa}"
LOCAL_ENV="${LOCAL_ENV:-backend/.env}"
KEYS=(LOMADEE_API_KEY LOMADEE_LINKS_API_KEY ADMIN_PASSWORD)

[ -f "$LOCAL_ENV" ] || { echo "Arquivo $LOCAL_ENV não encontrado."; exit 1; }

payload=""
for key in "${KEYS[@]}"; do
  line="$(grep -E "^${key}=" "$LOCAL_ENV" | tail -n 1 || true)"
  if [ -n "$line" ]; then
    payload+="${line}"$'\n'
    echo "enviando: ${key}"
  else
    echo "ausente no arquivo local (ignorada): ${key}"
  fi
done
[ -n "$payload" ] || { echo "Nada para enviar."; exit 1; }

printf '%s' "$payload" | ssh -i "$VPS_KEY" -o BatchMode=yes "$VPS_USER@$VPS_HOST" \
  "cd $VPS_DIR && touch .env && chmod 600 .env && while IFS= read -r line; do key=\"\${line%%=*}\"; grep -v \"^\${key}=\" .env > .env.tmp || true; printf '%s\n' \"\$line\" >> .env.tmp; mv .env.tmp .env; done && chmod 600 .env && echo 'segredos atualizados em .env (valores ocultos)'"
