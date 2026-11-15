# Mapa dos projetos: QuePromo e MercaGym

Leia isto antes de mexer em SEO, deploy ou Search Console. **São dois projetos, dois repositórios, dois domínios e duas formas de publicar.** Uma mudança num repositório não afeta o outro site.

## Visão geral

| | QuePromo | MercaGym |
|---|---|---|
| Domínio | `quepromo.com.br` | `mercagym.com.br` |
| Foco | Tudo das lojas (geral, inclui tênis) | Só treino/fitness (suplementos, moda e acessórios fitness) |
| Pasta local | `C:\Users\User\sopromoboa` | `C:\Users\User\buscafitness` |
| Repositório | `thiagovinigo/sopromoboa` | `thiagovinigo/mercagym` (privado) |
| `clickref` Awin | `quepromo` | `mercagym` |
| Frontend roda em | **VPS** (Docker, atrás do Traefik), desde 15/11/2026 | **VPS** (Docker, atrás do Traefik) |
| Backend roda em | **VPS**, `/opt/sopromoboa` | **VPS**, `/opt/mercagym` |
| Banco | `backend/sopromoboa.db` (volume na VPS) | `/data/mercagym.db` (volume na VPS) |

A VPS é a mesma para os dois (Locaweb, `191.252.191.189`, usuário `root`, chave `~/.ssh/buscarmas_vps`). Ela tem ~2 GB divididos com outros sites e o swap fica quase cheio. Cuidado com builds pesados lá.

O nome "sopromoboa" é o começo do QuePromo. A fase 1 do rename (marca, `utm_source`, pacote) está feita. Banco, pasta/volume/containers da VPS, repo do GitHub, chaves `sopromoboa_*_token` do navegador e IDs de afiliado seguem com o nome antigo de propósito: trocar sem migração perde comissão ou dados dos usuários.

## Como publicar

### QuePromo: backend (API + worker)
1. A partir da raiz: `.\scripts\deploy-backend.ps1`.
2. O script roda `pytest`, empacota `backend/` (sem `venv`, `.env` nem `*.db`), envia por `scp` e reinicia os containers `api` e `worker` na VPS com `backend/docker-compose.vps.yml` e `.env.vps`.
3. Não envia banco, então não sobrescreve produção.

### QuePromo: frontend (Next.js) — na VPS desde 15/11/2026
- **A Vercel não é mais usada.** Em 15/11/2026 o projeto `sopromoboa` passou a responder `402 DEPLOYMENT_DISABLED` (conta/time bloqueado) e o site ficou fora do ar. O frontend foi migrado para a VPS. Não republicar na Vercel.
- Roda em `/opt/quepromo-frontend` (container `quepromo-frontend`, `frontend/docker-compose.vps.yml`, imagem `quepromo-frontend:latest`). O Traefik atende `quepromo.com.br` (certificado próprio) e `www.quepromo.com.br` (301 para o apex, certificado próprio). Certificados separados de propósito: se um host não resolve, não bloqueia o outro.
- No servidor o frontend fala com a API pela rede interna (`INTERNAL_API_URL=http://sopromoboa-api-1:8000`); no navegador usa `NEXT_PUBLIC_API_URL=https://api.quepromo.com.br` (embutida no build, ver `frontend/Dockerfile`).
- **DNS (Registro.br):** `quepromo.com.br` A `191.252.191.189`; `www` CNAME `quepromo.com.br`; `api` A `191.252.191.189`. O painel recusa (HTTP 400) trocar um registro por outro na mesma gravação: remover e adicionar em gravações separadas.
- **Como publicar:** (1) `tar` de `frontend/` (sem `node_modules`, `.next`, `.vercel`) para `/opt/quepromo-frontend`; (2) rodar `./build.sh` lá (para o `sopromoboa-worker-1` durante o build, usa `DOCKER_BUILDKIT=0` com `--memory=650m` e heap de 420 MB, e religa o worker no fim); (3) `docker compose -f docker-compose.vps.yml up -d --no-build`; (4) **aquecer o sitemap** com `curl https://quepromo.com.br/sitemap.xml` (a primeira geração a frio leva 1 a 2 min com a VPS carregada; depois fica em ~0,6 s).
- **Não dá para construir a imagem no PC do dono:** o Norton Web/Mail Shield intercepta o HTTPS do Docker e o `npm ci` falha com `UNABLE_TO_VERIFY_LEAF_SIGNATURE`. Construir na VPS.
- A VPS tem ~2 GB, com pouca folga (≈470 MB livres e swap alto). Upgrade adiado pelo dono por 2 a 3 semanas (decisão de 15/11/2026).

### MercaGym (frontend, API e worker)
- Tudo roda em Docker na VPS (`mercagym-api`, `mercagym-worker-1`, `mercagym-frontend`) em `/opt/mercagym`.
- Deploy **pontual**: `tar` dos arquivos alterados por ssh e `docker compose build frontend` (ou os serviços afetados).
  - Frontend é imagem: precisa reconstruir. Use `DOCKER_BUILDKIT=0 docker build --memory=650m --memory-swap=900m` e pare só o worker do mercagym durante o build.
  - Variáveis do `.env` só recarregam com `docker compose up -d --force-recreate`.
- **Não usar `scripts/deploy-mercagym.ps1`.** O README do repositório diz que não é confiável, e a memória do projeto registra que ele já sobrescreveu o banco. Mesmo com a correção do commit `9cfd57f`, o procedimento acordado segue sendo o pontual.
- Segredos só em `backend/.env` na VPS (`chmod 600`). O código nunca leva valor padrão de segredo.
- Sem painel admin neste site, por decisão do dono.

## Search Console
Propriedades (prefixo de URL) na conta do dono:
- `https://quepromo.com.br/` e `https://mercagym.com.br/`.
- Existe também `buscaarmas.com.br` (propriedade de domínio). Não faz parte destes dois projetos. Não mexer sem perguntar.

URL direta do relatório de indexação: `https://search.google.com/search-console/index?resource_id=https%3A%2F%2F<dominio>%2F`.

Antes de "corrigir" algo no código por causa do Search Console, descubra **de qual site** é o problema e **em qual repositório** a correção deve entrar. Cada site tem robots, sitemap e metadados próprios.

## Estado do SEO (12/11/2026)
- Os dois `robots.txt` bloqueiam só `/r/`, `/api/` e (QuePromo) `/admin`. O `/r/` é o redirecionador de afiliado e o bloqueio é intencional. Não "corrigir".
- Maior parte dos não indexados é "Detectada, mas não indexada": 2.893 (MercaGym) e 5.692 (QuePromo). Não tem correção direta. Caminho: enxugar o sitemap e reforçar links internos.
- Sitemaps: MercaGym ~6.372 URLs, QuePromo ~28.479 URLs.
- Validações iniciadas em 12/11/2026: QuePromo 5xx (8) e 404 (102); MercaGym 404 (6) e soft 404 (11). Rever o relatório depois de alguns dias a duas semanas.
- QuePromo: `busca-personalizada` ganhou `noindex, follow` no commit `0ea8bb5`. **No ar desde 12/11/2026** (deploy `sopromoboa-gmq4m2lo9`, verificado com `curl`).
- MercaGym: já serve `noindex, follow` no `/?q=`. Essa correção vem do repositório dele, não do `sopromoboa`.

## Checklist antes de agir
1. Qual site? Qual repositório? (tabela acima)
2. Onde esse código roda? (VPS/Docker; a Vercel não é mais usada)
3. Como publica e o que isso arrisca? (banco, memória da VPS, segredos)
4. Depois de publicar, confirmar **no ar**, não só no commit:
   ```bash
   curl -s "https://quepromo.com.br/busca-personalizada?q=whey" | grep -o '<meta name="robots"[^>]*>'
   curl -s "https://mercagym.com.br/busca-personalizada?q=whey" | grep -o '<meta name="robots"[^>]*>'
   ```
5. Só validar no Search Console depois que a correção estiver no ar.

## Invariantes (valem para os dois)
- URLs de produto são páginas diretas (sem busca, sem placeholder). Tags de afiliado do dono (Amazon, Mercado Livre, Shopee) são força-aplicadas. Ver `CLAUDE.md`.
- Admin do QuePromo falha fechado sem `ADMIN_PASSWORD`.
- Nunca commitar `.env`, `*.db`, chaves ou tokens.
